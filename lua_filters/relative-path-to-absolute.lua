-- Pandoc Lua Filter to convert relative paths in Link and Image elements
-- to absolute web root paths (e.g., from 'img/x.jpg' to '/img/x.jpg').
-- This ensures assets are correctly referenced on the deployed website regardless of the HTML file's location.

-- Function to check if a path is relative
local function is_relative(url)
  -- A path is considered relative if it does not start with:
  -- 1. A scheme (http, https, mailto, etc.)
  -- 2. A leading slash (absolute path from web root /)
  -- 3. A fragment identifier (#)
  return url and not (url:match("^%a+://") or url:match("^/") or url:match("^#"))
end

-- Function to prepend the web root path ('/') to a relative URL
local function prepend_web_root(url)
  if is_relative(url) then
    -- Prepend '/' to make it root-absolute
    return "/" .. url
  end
  return url
end

-- Process images
function Image(el)
  el.src = prepend_web_root(el.src)
  return el
end

-- Process links
function Link(el)
  el.target = prepend_web_root(el.target)
  return el
end