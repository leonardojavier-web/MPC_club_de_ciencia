import { useState } from 'react';
import { postChatMessage } from '../services/api';

const initialMessages = [
  { role: 'assistant', content: '¡Hola! Soy tu asistente historiador de Las Varillas. ¿En qué puedo ayudarte hoy?' },
];

export function useChat({ postMessage = postChatMessage } = {}) {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [thinkingMessage, setThinkingMessage] = useState('');

  const sendMessage = async () => {
    const userMessage = input.trim();
    if (!userMessage || isLoading) return;

    setMessages((current) => [...current, { role: 'user', content: userMessage }]);
    setInput('');
    setIsLoading(true);
    setThinkingMessage('Consultando al asistente...');

    try {
      const reply = await postMessage(userMessage);
      setMessages((current) => [...current, { role: 'assistant', content: reply }]);
    } catch (error) {
      const detail = error.response?.data?.detail || error.message;
      setMessages((current) => [...current, { role: 'assistant', content: `Error: ${detail}` }]);
    } finally {
      setIsLoading(false);
      setThinkingMessage('');
    }
  };

  return { messages, input, setInput, isLoading, thinkingMessage, sendMessage };
}