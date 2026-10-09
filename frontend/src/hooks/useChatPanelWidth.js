import { useEffect, useState } from 'react';

const MIN_WIDTH = 300;
const MAX_WIDTH = 560;
const STORAGE_KEY = 'historia-chat-width';

export function useChatPanelWidth() {
  const [chatWidth, setChatWidth] = useState(() => {
    const savedWidth = Number(localStorage.getItem(STORAGE_KEY));
    return savedWidth >= MIN_WIDTH && savedWidth <= MAX_WIDTH ? savedWidth : 380;
  });
  const [isResizing, setIsResizing] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(chatWidth));
  }, [chatWidth]);

  useEffect(() => {
    if (!isResizing) return undefined;

    const handlePointerMove = (event) => {
      const maximumWidth = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, window.innerWidth - 260));
      const nextWidth = Math.min(maximumWidth, Math.max(MIN_WIDTH, window.innerWidth - event.clientX));
      setChatWidth(nextWidth);
    };
    const stopResizing = () => setIsResizing(false);

    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', stopResizing, { once: true });
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', stopResizing);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  const startResize = (event) => {
    event.preventDefault();
    setIsResizing(true);
  };

  const resizeBy = (delta) => {
    setChatWidth((currentWidth) => Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, currentWidth + delta)));
  };

  return { chatWidth, isResizing, startResize, resizeBy };
}