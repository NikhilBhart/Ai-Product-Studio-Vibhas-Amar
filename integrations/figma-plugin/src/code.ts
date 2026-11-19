// Starter only: import a generated design JSON payload into the currently open Figma file.
// Build with the Figma plugin toolchain and run from Figma's development plugin menu.
figma.showUI(__html__, { width: 360, height: 480 });

type DesignPayload = { name: string; screens: Array<{ name: string; width?: number; height?: number; background?: string }> };
figma.ui.onmessage = async (message: { type: string; payload?: DesignPayload }) => {
  if (message.type !== 'IMPORT_DESIGN' || !message.payload) return;
  const page = figma.currentPage;
  page.name = message.payload.name || 'AI Product Studio';
  let x = 0;
  for (const screen of message.payload.screens ?? []) {
    const frame = figma.createFrame();
    frame.name = screen.name;
    frame.resize(screen.width ?? 1440, screen.height ?? 900);
    frame.x = x; frame.y = 0;
    frame.fills = [{ type: 'SOLID', color: hexToRgb(screen.background ?? '#F5F6F1') }];
    const title = figma.createText();
    title.characters = screen.name;
    title.x = 48; title.y = 42;
    frame.appendChild(title);
    x += frame.width + 80;
  }
  figma.notify('Imported starter frames. Add components and detailed layouts in the next design pass.');
};

function hexToRgb(hex: string) {
  const value = hex.replace('#', '');
  return { r: parseInt(value.slice(0, 2), 16) / 255, g: parseInt(value.slice(2, 4), 16) / 255, b: parseInt(value.slice(4, 6), 16) / 255 };
}
