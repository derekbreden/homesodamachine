// Inline this source in the fragment; it has no imports or runtime requests.
function createInlineMobileTheme(root) {
  if (!root?.id) throw new Error('The visualization needs a unique root ID');
  const probe = document.createElement('span');
  probe.setAttribute('aria-hidden', 'true');
  probe.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;pointer-events:none';
  const style = document.createElement('style');
  const selector = '#' + CSS.escape(root.id);
  style.textContent = `${selector},${selector} *{-webkit-text-fill-color:currentColor}`;
  root.append(probe, style);
  root.style.color = 'var(--foreground,CanvasText)';

  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 1;
  const context = canvas.getContext('2d', {willReadFrequently: true});
  let host;
  let colors = {};

  function sample(value) {
    if (!value) return null;
    for (const candidate of [value, `hsl(${value})`, `rgb(${value})`]) {
      if (!CSS.supports('color', candidate)) continue;
      probe.style.color = candidate;
      context.clearRect(0, 0, 1, 1);
      context.fillStyle = 'transparent';
      context.fillStyle = getComputedStyle(probe).color;
      context.fillRect(0, 0, 1, 1);
      const rgba = Array.from(context.getImageData(0, 0, 1, 1).data);
      if (rgba[3]) return {rgba, css: `rgba(${rgba[0]},${rgba[1]},${rgba[2]},${rgba[3] / 255})`};
    }
    return null;
  }

  function pick(names, fallback, chromatic = false, opaque = true) {
    for (const value of [...names.map(name => host.getPropertyValue(`--${name}`).trim()), fallback]) {
      const color = sample(value);
      if (color && (!opaque || color.rgba[3] >= 250) &&
          (!chromatic || Math.max(...color.rgba.slice(0, 3)) - Math.min(...color.rgba.slice(0, 3)) >= 20)) {
        return color;
      }
    }
    return sample(fallback);
  }

  function luminance(color) {
    return color.rgba.slice(0, 3).map(value => {
      value /= 255;
      return value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4;
    }).reduce((sum, value, index) => sum + value * [.2126, .7152, .0722][index], 0);
  }

  function contrast(a, b) {
    const x = luminance(a), y = luminance(b);
    return (Math.max(x, y) + .05) / (Math.min(x, y) + .05);
  }

  function readable(foreground, background) {
    if (contrast(foreground, background) >= 4.5) return foreground;
    return [sample('CanvasText'), sample('Canvas')]
      .sort((a, b) => contrast(b, background) - contrast(a, background))[0];
  }

  function refresh() {
    // Read outside the fragment so resolved overrides cannot feed back into the source palette.
    host = getComputedStyle(root.parentElement);
    let background;
    for (let element = root.parentElement; element; element = element.parentElement) {
      const color = sample(getComputedStyle(element).backgroundColor);
      if (color?.rgba[3] >= 250) { background = color; break; }
    }
    background ||= sample('Canvas');
    const foreground = readable(pick(['foreground', 'color-text-primary'], 'CanvasText'), background);
    colors = {
      foreground,
      background,
      'muted-foreground': pick(['muted-foreground', 'color-text-secondary'], foreground.css, false, false)
    };

    const fallbacks = ['blue', 'orange', 'green', 'purple', 'purple', 'green'];
    for (let index = 1; index <= 6; index++) {
      colors[`viz-series-${index}`] = pick([`viz-series-${index}`, fallbacks[index - 1]], 'LinkText', true);
    }

    // Normalize the text/surface pairs used by the inline renderer's native controls and cards.
    for (const name of ['card', 'popover', 'secondary', 'accent', 'primary']) {
      colors[name] = pick([name], name === 'primary' ? foreground.css : background.css);
      colors[name + '-foreground'] = readable(pick([name + '-foreground'], foreground.css), colors[name]);
    }
    for (const name of ['border', 'input', 'ring']) colors[name] = pick([name], foreground.css, false, false);
    for (const name of ['blue', 'orange', 'green', 'red', 'purple', 'yellow']) colors[name] = pick([name], 'LinkText', true);
    for (const [name, color] of Object.entries(colors)) root.style.setProperty(`--${name}`, color.css);
    const aliases = {
      'color-text-primary': 'foreground', 'color-text-secondary': 'muted-foreground',
      'color-background-primary': 'background', 'color-background-secondary': 'secondary',
      'color-text-inverse': 'primary-foreground', 'color-text-info': 'viz-series-1',
      'color-background-info': 'accent', 'color-border-primary': 'input',
      'color-border-secondary': 'border', 'color-ring-primary': 'ring'
    };
    for (const [name, target] of Object.entries(aliases)) root.style.setProperty(`--${name}`, colors[target].css);
    return api;
  }

  function get(token) {
    return colors[token] || (colors[token] = pick([token], colors.foreground.css, false, false));
  }

  function observe(onChange) {
    const changed = () => { refresh(); onChange(api); };
    const attributes = new MutationObserver(changed);
    for (let element = root.parentElement; element; element = element.parentElement) {
      attributes.observe(element, {attributes: true, attributeFilter: ['class', 'style', 'data-theme']});
    }
    const stylesheet = new MutationObserver(changed);
    stylesheet.observe(document.head, {childList: true, subtree: true, characterData: true});
    const media = matchMedia('(prefers-color-scheme:dark)');
    media.addEventListener('change', changed);
    return () => { attributes.disconnect(); stylesheet.disconnect(); media.removeEventListener('change', changed); };
  }

  const api = {refresh, cssColor: token => get(token).css, rgba: token => get(token).rgba.slice(), observe};
  return refresh();
}
