from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import analyze_and_concat_v3 as v3

FFMPEG_CMD = "ffmpeg"
TRANSITION_CLIP_NAME = "transition_black_1s.mp4"

# xfade がサポートしている代表的なトランジション
XF_TRANSITIONS = [
    "fade",
    "fadeblack",
    "fadewhite",
    "wipeleft",
    "wiperight",
    "wipeup",
    "wipedown",
    "slideleft",
    "slideright",
    "slideup",
    "slidedown",
    "circleopen",
    "circleclose",
    "vertopen",
    "vertclose",
    "horzopen",
    "horzclose",
    "radial",
    "smoothleft",
    "smoothright",
    "smoothup",
    "smoothdown",
]


class SmartVideoConcatV3GUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("smart_video_concat v3 GUI")
        self.geometry("880x640")

        self.files: list[Path] = []
        # 0 始まりインデックス: 0 → 1 本目の「直後」
        self.transition_after_indices: set[int] = set()

        self.output_path_var = tk.StringVar()
        self.crf_var = tk.StringVar(value="20")
        self.width_var = tk.StringVar(value="1920")
        self.height_var = tk.StringVar(value="1080")
        self.preset_var = tk.StringVar(value="veryfast")
        self.transition_type_var = tk.StringVar(value="fade")

        self.file_listbox: tk.Listbox
        self.log_text: tk.Text

        self._build_ui()

    # ================= UI =================

    def _build_ui(self) -> None:
        frame_top = ttk.LabelFrame(self, text="入力ファイル一覧（現在の表示順 = 連結順）")
        frame_top.pack(fill="both", expand=True, padx=10, pady=8)

        left = ttk.Frame(frame_top)
        left.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=8)

        scrollbar = ttk.Scrollbar(left, orient="vertical")
        self.file_listbox = tk.Listbox(
            left,
            selectmode="extended",
            yscrollcommand=scrollbar.set,
            height=12,
        )
        scrollbar.config(command=self.file_listbox.yview)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        right = ttk.Frame(frame_top)
        right.pack(side="left", fill="y", padx=(4, 8), pady=8)

        ttk.Button(right, text="追加# CODE_TRUNCATED", command=self.on_add_files).pack(fill="x", pady=2)
        ttk.Button(right, text="選択削除", command=self.on_remove_selected).pack(fill="x", pady=2)
        ttk.Button(right, text="全クリア", command=self.on_clear_files).pack(fill="x", pady=2)
        ttk.Button(right, text="上へ (表示順)", command=self.on_move_up).pack(fill="x", pady=2)
        ttk.Button(right, text="下へ (表示順)", command=self.on_move_down).pack(fill="x", pady=2)

        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=4)

        ttk.Button(
            right,
            text="選択の後に\nトランジション(黒)",
            command=self.on_add_transition_after_selected,
        ).pack(fill="x", pady=2)
        ttk.Button(
            right,
            text="トランジション\n全クリア",
            command=self.on_clear_transitions,
        ).pack(fill="x", pady=2)

        frame_mid = ttk.LabelFrame(self, text="エンコード / トランジション設定")
        frame_mid.pack(fill="x", padx=10, pady=4, ipady=4)

        grid = ttk.Frame(frame_mid)
        grid.pack(fill="x", padx=8, pady=4)

        # 1 行目: CRF / preset
        ttk.Label(grid, text="CRF").grid(row=0, column=0, sticky="w", padx=2, pady=2)
        ttk.Entry(grid, textvariable=self.crf_var, width=8).grid(row=0, column=1, sticky="w", padx=2, pady=2)
        ttk.Label(grid, text="preset").grid(row=0, column=2, sticky="w", padx=12, pady=2)
        preset_combo = ttk.Combobox(
            grid,
            textvariable=self.preset_var,
            values=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium"],
            width=12,
            state="readonly",
        )
        preset_combo.grid(row=0, column=3, sticky="w", padx=2, pady=2)
        preset_combo.current(2)

        # 2 行目: width / height
        ttk.Label(grid, text="幅 (width)").grid(row=1, column=0, sticky="w", padx=2, pady=2)
        ttk.Entry(grid, textvariable=self.width_var, width=8).grid(row=1, column=1, sticky="w", padx=2, pady=2)
        ttk.Label(grid, text="高さ (height)").grid(row=1, column=2, sticky="w", padx=12, pady=2)
        ttk.Entry(grid, textvariable=self.height_var, width=8).grid(row=1, column=3, sticky="w", padx=2, pady=2)

        # 3 行目: トランジション種別 (xfade)
        ttk.Label(grid, text="トランジション種別 (xfade)").grid(row=2, column=0, sticky="w", padx=2, pady=2)
        tr_combo = ttk.Combobox(
            grid,
            textvariable=self.transition_type_var,
            values=XF_TRANSITIONS,
            width=18,
            state="readonly",
        )
        tr_combo.grid(row=2, column=1, columnspan=3, sticky="w", padx=2, pady=2)
        tr_combo.current(0)

        # 出力パス
        frame_out = ttk.Frame(frame_mid)
        frame_out.pack(fill="x", padx=8, pady=(2, 6))
        ttk.Label(frame_out, text="出力ファイル").pack(side="left")
        ttk.Entry(frame_out, textvariable=self.output_path_var).pack(
            side="left", fill="x", expand=True, padx=6
        )
        ttk.Button(frame_out, text="参照# CODE_TRUNCATED", command=self.on_browse_output).pack(side="left")

        frame_bottom = ttk.Frame(self)
        frame_bottom.pack(fill="both", expand=False, padx=10, pady=(4, 10))

        btn_row = ttk.Frame(frame_bottom)
        btn_row.pack(fill="x", pady=(0, 6))

        ttk.Button(
            btn_row,
            text="自動並び替え (v3 推奨順)",
            command=self.on_auto_order_v3,
        ).pack(side="left")

        ttk.Button(
            btn_row,
            text="全区間クロスフェードで連結",
            command=self.on_run_full_crossfade,
        ).pack(side="left", padx=8)

        ttk.Button(
            btn_row,
            text="連結を実行（表示順のまま）",
            command=self.on_run_concat,
        ).pack(side="right")

        self.log_text = tk.Text(frame_bottom, height=12, wrap="word")
        self.log_text.pack(fill="both", expand=True)
        self._log("smart_video_concat v3 GUI を起動しました。")
        self._log("・通常ボタン: 2 本 + 1 箇所指定ならクロスフェード、それ以外は黒トランジション + concat。")
        self._log("・全区間クロスフェード: すべての境界を xfade（選択した transition 種別）で連結します。")

    # ================= ファイルリスト操作 =================

    def _refresh_listbox(self) -> None:
        self.file_listbox.delete(0, tk.END)
        for p in self.files:
            self.file_listbox.insert(tk.END, str(p))

    def _invalidate_transitions_due_to_reorder(self) -> None:
        if self.transition_after_indices:
            self.transition_after_indices.clear()
            self._log("順序変更のため、トランジション指定をリセットしました。")

    def on_add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="連結候補の mp4 ファイルを選択",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
        )
        if not paths:
            return
        for p in paths:
            path_obj = Path(p)
            if path_obj.is_file():
                self.files.append(path_obj)
        self._refresh_listbox()
        self._log(f"{len(paths)} 個のファイルを追加しました。")

        if self.files and not self.output_path_var.get():
            first_dir = self.files[0].parent
            self.output_path_var.set(str(first_dir / "smart_concat_v3_gui.mp4"))

    def on_remove_selected(self) -> None:
        sel = list(self.file_listbox.curselection())
        if not sel:
            return
        for idx in reversed(sel):
            if 0 <= idx < len(self.files):
                self.files.pop(idx)
        self._refresh_listbox()
        self._invalidate_transitions_due_to_reorder()
        self._log("選択中のファイルを削除しました。")

    def on_clear_files(self) -> None:
        if not self.files:
            return
        self.files.clear()
        self._refresh_listbox()
        self.transition_after_indices.clear()
        self._log("ファイルとトランジション指定をすべてクリアしました。")

    def on_move_up(self) -> None:
        sel = list(self.file_listbox.curselection())
        if not sel:
            return
        for idx in sel:
            if idx <= 0:
                continue
            self.files[idx - 1], self.files[idx] = self.files[idx], self.files[idx - 1]
        self._refresh_listbox()
        self.file_listbox.selection_clear(0, tk.END)
        for idx in [max(i - 1, 0) for i in sel]:
            self.file_listbox.selection_set(idx)
        self._invalidate_transitions_due_to_reorder()

    def on_move_down(self) -> None:
        sel = list(self.file_listbox.curselection())
        if not sel:
            return
        for idx in reversed(sel):
            if idx >= len(self.files) - 1:
                continue
            self.files[idx + 1], self.files[idx] = self.files[idx], self.files[idx + 1]
        self._refresh_listbox()
        self.file_listbox.selection_clear(0, tk.END)
        for idx in [min(i + 1, len(self.files) - 1) for i in sel]:
            self.file_listbox.selection_set(idx)
        self._invalidate_transitions_due_to_reorder()

    # ================= 出力パス =================

    def on_browse_output(self) -> None:
        initialdir = str(self.files[0].parent) if self.files else None
        path = filedialog.asksaveasfilename(
            title="出力 mp4 ファイルを指定",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            initialdir=initialdir,
            initialfile="smart_concat_v3_gui.mp4",
        )
        if path:
            self.output_path_var.set(path)

    # ================= 自動並び替え (v3) =================

    def on_auto_order_v3(self) -> None:
        if not self.files:
            messagebox.showwarning("警告", "自動並び替えの対象となるファイルがありません。")
            return
        self._log("特徴抽出と順序推定を開始します (v3)# CODE_TRUNCATED")
        feats: list[dict] = []
        for p in self.files:
            self._log(f"特徴抽出: {p}")
            s, e = v3.extract_features(str(p))
            feats.append({"path": p, "start": s, "end": e})
        order = v3.build_order(feats)
        ordered = [feats[i]["path"] for i in order]
        self.files = ordered
        self._refresh_listbox()
        self._invalidate_transitions_due_to_reorder()
        self._log("推定された連結順 (先頭 -> 末尾):")
        for i, p in enumerate(self.files, 1):
            self._log(f"{i:2d}. {p}")
        self._log("自動並び替え (v3 推奨順) を適用しました。")

    # ================= トランジション指定（黒クリップ用） =================

    def on_add_transition_after_selected(self) -> None:
        if not self.files:
            messagebox.showwarning("警告", "トランジションを挿入する前にファイルを追加してください。")
            return
        sel = list(self.file_listbox.curselection())
        if not sel:
            messagebox.showwarning("警告", "少なくとも 1 行選択してください。")
            return
        for idx in sel:
            if 0 <= idx < len(self.files):
                self.transition_after_indices.add(idx)
        self._log("黒 1 秒トランジションを挿入する位置（1 始まり）:")
        for idx in sorted(self.transition_after_indices):
            if idx < len(self.files):
                self._log(f" - {idx + 1} 番目の直後")

    def on_clear_transitions(self) -> None:
        if not self.transition_after_indices:
            return
        self.transition_after_indices.clear()
        self._log("トランジション指定を全クリアしました。")

    # ================= ffprobe ヘルパ =================

    def _probe_duration(self, path: Path) -> float | None:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            self._log("ffprobe が見つかりません。", error=True)
            return None
        if proc.returncode != 0:
            self._log("ffprobe による長さ取得に失敗しました。", error=True)
            self._log(proc.stderr)
            return None
        try:
            return float(proc.stdout.strip())
        except ValueError:
            self._log("ffprobe 出力の解釈に失敗しました。", error=True)
            return None

    def _has_audio_stream(self, path: Path) -> bool:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a",
            "-show_entries", "stream=index",
            "-of", "csv=p=0",
            str(path),
        ]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            self._log("ffprobe が見つからないため音声有無を判定できません。", error=True)
            return False
        if proc.returncode != 0:
            self._log("ffprobe による音声判定に失敗しました。", error=True)
            self._log(proc.stderr)
            return False
        return bool(proc.stdout.strip())

    # ================= 2 クリップ専用クロスフェード（通常ボタン用） =================

    def _run_ffmpeg_crossfade_two(
        self,
        input_paths: list[Path],
        output_path: Path,
        crf: int,
        preset: str,
        width: int,
        height: int,
    ) -> bool:
        if len(input_paths) != 2:
            return False
        clip0, clip1 = input_paths
        self._log("2 クリップ専用クロスフェードを試みます。")

        d0 = self._probe_duration(clip0)
        d1 = self._probe_duration(clip1)
        if d0 is None or d1 is None:
            self._log("長さ取得に失敗したためクロスフェードをスキップします。", error=True)
            return False

        max_t = 1.0
        t = min(max_t, d0 / 2.0, d1 / 2.0)
        if t <= 0.1:
            self._log("クロスフェード時間が確保できないためスキップします。", error=True)
            return False
        offset = max(d0 - t, 0.0)

        has_a0 = self._has_audio_stream(clip0)
        has_a1 = self._has_audio_stream(clip1)
        tr = self.transition_type_var.get().strip() or "fade"
        if tr not in XF_TRANSITIONS:
            tr = "fade"

        self._log(f"clip0={d0:.3f}s, clip1={d1:.3f}s, t={t:.3f}s, offset={offset:.3f}s")
        self._log(f"audio: clip0={has_a0}, clip1={has_a1}, transition={tr}")

        t_str = f"{t:.3f}"
        offset_str = f"{offset:.3f}"

        vf = (
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,"
            "setpts=PTS-STARTPTS[v0];"
            f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,"
            "setpts=PTS-STARTPTS[v1];"
        )

        if has_a0 and has_a1:
            af = "[0:a]asetpts=PTS-STARTPTS[a0];[1:a]asetpts=PTS-STARTPTS[a1];"
            xf = (
                f"[v0][v1]xfade=transition={tr}:duration={t_str}:offset={offset_str}[vxf];"
                "[vxf]format=yuv420p[vout];"
                f"[a0][a1]acrossfade=d={t_str}[aout]"
            )
            filter_complex = vf + af + xf
            cmd = [
                FFMPEG_CMD, "-y",
                "-i", str(clip0),
                "-i", str(clip1),
                "-filter_complex", filter_complex,
                "-map", "[vout]",
                "-map", "[aout]",
                "-c:v", "libx264",
                "-preset", preset,
                "-crf", str(crf),
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                str(output_path),
            ]
        else:
            self._log("音声ストリームが揃っていないため映像のみクロスフェードします。")
            xf = (
                f"[v0][v1]xfade=transition={tr}:duration={t_str}:offset={offset_str}[vxf];"
                "[vxf]format=yuv420p[vout]"
            )
            filter_complex = vf + xf
            cmd = [
                FFMPEG_CMD, "-y",
                "-i", str(clip0),
                "-i", str(clip1),
                "-filter_complex", filter_complex,
                "-map", "[vout]",
                "-c:v", "libx264",
                "-preset", preset,
                "-crf", str(crf),
                "-pix_fmt", "yuv420p",
                "-an",
                "-movflags", "+faststart",
                str(output_path),
            ]

        self._log("ffmpeg クロスフェードコマンド:")
        self._log(" ".join(cmd))

        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            self._log("ffmpeg が見つかりません。", error=True)
            messagebox.showerror("エラー", "ffmpeg が見つかりませんでした。PATH を確認してください。")
            return False

        if proc.returncode != 0:
            self._log("クロスフェードの実行に失敗しました。", error=True)
            self._log(proc.stderr)
            messagebox.showerror("エラー", "クロスフェードの実行に失敗しました。ログを確認してください。")
            return False

        self._log("クロスフェードが正常に完了しました。")
        self._log(proc.stderr)
        messagebox.showinfo("完了", f"クロスフェード連結が完了しました。\n出力: {output_path}")
        return True

    # ================= 全区間クロスフェード（N 本） =================

    def _run_ffmpeg_full_crossfade_chain(
        self,
        input_paths: list[Path],
        output_path: Path,
        crf: int,
        preset: str,
        width: int,
        height: int,
        transition: str,
    ) -> None:
        n = len(input_paths)
        if n < 2:
            messagebox.showwarning("警告", "全区間クロスフェードには 2 本以上のクリップが必要です。")
            return

        # 長さ取得
        durations: list[float] = []
        for p in input_paths:
            d = self._probe_duration(p)
            if d is None:
                self._log(f"長さ取得失敗: {p}", error=True)
                messagebox.showerror("エラー", f"長さ取得に失敗したファイルがあります: {p}")
                return
            durations.append(d)

        min_d = min(durations)
        max_t = 1.0
        t = min(max_t, min_d / 2.0)
        if t <= 0.1:
            self._log("クロスフェード時間が確保できないため中止します。", error=True)
            messagebox.showerror("エラー", "クロスフェード時間を十分に確保できませんでした。")
            return

        # 累積長さ → offset 計算
        prefix = []
        acc = 0.0
        for d in durations:
            acc += d
            prefix.append(acc)
        offsets = []
        for j in range(n - 1):
            off = prefix[j] - (j + 1) * t
            if off < 0:
                off = 0.0
            offsets.append(off)

        self._log("全区間クロスフェード用 長さ / offset:")
        for i, d in enumerate(durations):
            self._log(f" clip{i}: {d:.3f}s")
        for j, off in enumerate(offsets):
            self._log(f" fade{j}: offset={off:.3f}s")

        # 音声ストリーム確認
        audio_flags = [self._has_audio_stream(p) for p in input_paths]
        has_any_audio = any(audio_flags)
        audio_all = all(audio_flags) and has_any_audio

        if not has_any_audio:
            self._log("音声ストリームなし → 映像のみクロスフェード。")
        elif not audio_all:
            self._log("音声ストリームが揃っていないため、全区間クロスフェードでは音声なしで出力します。", error=True)
            self._log(f"audio flags: {audio_flags}")
        else:
            self._log("全クリップに音声ストリームあり → 映像 + 音声クロスフェード。")

        t_str = f"{t:.3f}"

        parts: list[str] = []

        # 入力ごとの前処理
        for i in range(n):
            parts.append(
                f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,"
                f"setpts=PTS-STARTPTS[v{i}];"
            )
            if audio_all:
                parts.append(f"[{i}:a]asetpts=PTS-STARTPTS[a{i}];")

        prev_v = "v0"
        prev_a = "a0" if audio_all else None

        for j in range(n - 1):
            off_str = f"{offsets[j]:.3f}"
            vout = f"vxf{j}"
            parts.append(
                f"[{prev_v}][v{j+1}]xfade=transition={transition}:duration={t_str}:offset={off_str}[{vout}];"
            )
            prev_v = vout
            if audio_all and prev_a is not None:
                aout = f"axf{j}"
                parts.append(f"[{prev_a}][a{j+1}]acrossfade=d={t_str}[{aout}];")
                prev_a = aout

        parts.append(f"[{prev_v}]format=yuv420p[vout];")
        aout_label = prev_a if audio_all and prev_a is not None else None

        filter_complex = "".join(parts)

        cmd: list[str] = [FFMPEG_CMD, "-y"]
        for p in input_paths:
            cmd.extend(["-i", str(p)])
        cmd.extend(["-filter_complex", filter_complex, "-map", "[vout]"])
        cmd.extend(["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p"])
        if aout_label is not None:
            cmd.extend(["-map", f"[{aout_label}]", "-c:a", "aac", "-b:a", "192k"])
        else:
            cmd.extend(["-an"])
        cmd.extend(["-movflags", "+faststart", str(output_path)])

        self._log("ffmpeg 全区間クロスフェードコマンド:")
        self._log(" ".join(cmd))

        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            self._log("ffmpeg が見つかりません。", error=True)
            messagebox.showerror("エラー", "ffmpeg が見つかりませんでした。PATH を確認してください。")
            return

        if proc.returncode != 0:
            self._log("全区間クロスフェードの実行に失敗しました。", error=True)
            self._log(proc.stderr)
            messagebox.showerror("エラー", "全区間クロスフェードの実行に失敗しました。ログを確認してください。")
            return

        self._log("全区間クロスフェードが正常に完了しました。")
        self._log(proc.stderr)
        messagebox.showinfo("完了", f"全区間クロスフェード連結が完了しました。\n出力: {output_path}")

    # ================= 黒トランジション用クリップ生成 =================

    def _ensure_transition_clip(self) -> Path | None:
        base_dir = Path(__file__).resolve().parent
        clip_path = base_dir / TRANSITION_CLIP_NAME
        if clip_path.exists():
            return clip_path

        self._log("黒 1 秒トランジションクリップを新規作成します。")
        cmd = [
            FFMPEG_CMD,
            "-y",
            "-f", "lavfi",
            "-i", "color=c=black:s=1920x1080:d=1",
            "-r", "30",
            "-pix_fmt", "yuv420p",
            str(clip_path),
        ]
        self._log(" ".join(cmd))
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            self._log("ffmpeg が見つからないため黒クリップを生成できません。", error=True)
            messagebox.showerror("エラー", "ffmpeg が見つからないため黒クリップを生成できませんでした。")
            return None
        if proc.returncode != 0:
            self._log("黒クリップ生成に失敗しました。", error=True)
            self._log(proc.stderr)
            messagebox.showerror("エラー", "黒クリップ生成に失敗しました。ログを確認してください。")
            return None
        self._log(f"黒クリップを作成しました: {clip_path}")
        return clip_path

    # ================= 通常 concat 実行 =================

    def _run_ffmpeg_concat(
        self,
        input_paths: list[Path],
        output_path: Path,
        crf: int,
        preset: str,
        width: int,
        height: int,
    ) -> None:
        # 2 本 + 1 箇所指定 (1 本目の後) → クロスフェード優先
        if len(input_paths) == 2 and self.transition_after_indices == {0}:
            self._log("2 本かつ 1 箇所指定なので、クロスフェードモードを優先します。")
            if self._run_ffmpeg_crossfade_two(
                input_paths=input_paths,
                output_path=output_path,
                crf=crf,
                preset=preset,
                width=width,
                height=height,
            ):
                return
            self._log("クロスフェード失敗のため、通常 concat にフォールバックします。", error=True)

        tmp_dir = Path(tempfile.mkdtemp(prefix="svc_v3_gui_"))
        concat_path = tmp_dir / "concat_list_v3.txt"

        trans_clip: Path | None = None
        if self.transition_after_indices:
            trans_clip = self._ensure_transition_clip()
            if trans_clip is None:
                self._log("黒クリップ準備に失敗したためトランジションなしで連結します。", error=True)
                self.transition_after_indices.clear()

        with concat_path.open("w", encoding="utf-8") as f:
            for idx, p in enumerate(input_paths):
                posix = p.as_posix().replace("'", "''")
                f.write(f"file '{posix}'\n")
                if trans_clip is not None and idx in self.transition_after_indices:
                    t_posix = trans_clip.as_posix().replace("'", "''")
                    f.write(f"file '{t_posix}'\n")

        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p"
        )

        cmd = [
            FFMPEG_CMD,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_path),
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", str(crf),
            "-c:a", "copy",
            str(output_path),
        ]

        self._log("ffmpeg concat コマンド:")
        self._log(" ".join(cmd))

        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            self._log("ffmpeg が見つかりません。", error=True)
            messagebox.showerror("エラー", "ffmpeg が見つかりませんでした。PATH を確認してください。")
            return

        if proc.returncode != 0:
            self._log("ffmpeg の実行に失敗しました。", error=True)
            self._log(proc.stderr)
            messagebox.showerror("エラー", "ffmpeg の実行に失敗しました。ログを確認してください。")
            return

        self._log("concat 連結が完了しました。")
        self._log(proc.stderr)
        messagebox.showinfo("完了", f"連結が完了しました。\n出力: {output_path}")

    # ================= ボタンクリック: 通常 / 全区間クロスフェード =================

    def on_run_concat(self) -> None:
        if not self.files:
            messagebox.showwarning("警告", "連結する mp4 ファイルを 1 つ以上追加してください。")
            return

        output_str = self.output_path_var.get().strip()
        if not output_str:
            messagebox.showwarning("警告", "出力ファイルを指定してください。")
            return

        try:
            crf = int(self.crf_var.get().strip())
            width = int(self.width_var.get().strip())
            height = int(self.height_var.get().strip())
        except ValueError:
            messagebox.showwarning("警告", "CRF / 幅 / 高さには整数を入力してください。")
            return

        preset = self.preset_var.get().strip() or "veryfast"
        output_path = Path(output_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._log("通常モードで連結を開始します。")
        self._log(f"入力数={len(self.files)}, 出力={output_path}, CRF={crf}, preset={preset}, size={width}x{height}")
        if self.transition_after_indices:
            s = ", ".join(str(i + 1) for i in sorted(self.transition_after_indices) if i < len(self.files))
            self._log(f"黒トランジション挿入位置 (1 始まり): {s}")
        else:
            self._log("黒トランジション挿入なし。")

        self._run_ffmpeg_concat(list(self.files), output_path, crf, preset, width, height)

    def on_run_full_crossfade(self) -> None:
        if len(self.files) < 2:
            messagebox.showwarning("警告", "全区間クロスフェードには 2 本以上のクリップが必要です。")
            return

        output_str = self.output_path_var.get().strip()
        if not output_str:
            messagebox.showwarning("警告", "出力ファイルを指定してください。")
            return

        try:
            crf = int(self.crf_var.get().strip())
            width = int(self.width_var.get().strip())
            height = int(self.height_var.get().strip())
        except ValueError:
            messagebox.showwarning("警告", "CRF / 幅 / 高さには整数を入力してください。")
            return

        preset = self.preset_var.get().strip() or "veryfast"
        tr = self.transition_type_var.get().strip() or "fade"
        if tr not in XF_TRANSITIONS:
            tr = "fade"

        output_path = Path(output_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._log("全区間クロスフェードモードで連結を開始します。")
        self._log(f"入力数={len(self.files)}, 出力={output_path}")
        self._log(f"CRF={crf}, preset={preset}, size={width}x{height}, transition={tr}")
        self._log("画面上の順序のすべての境界をクロスフェードします（黒トランジション指定は無視されます）。")

        self._run_ffmpeg_full_crossfade_chain(
            list(self.files),
            output_path,
            crf,
            preset,
            width,
            height,
            tr,
        )

    # ================= ログ =================

    def _log(self, msg: str, error: bool = False) -> None:
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        # error フラグは今のところ色分け等には使っていないが、将来拡張用に残す


def main() -> None:
    app = SmartVideoConcatV3GUI()
    app.mainloop()


if __name__ == "__main__":
    main()
