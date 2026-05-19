import { useState, useEffect, useRef } from "react";

export function useTypingEffect(
  text: string,
  enabled: boolean = true,
  minSpeedMs: number = 5,
  maxSpeedMs: number = 25
) {
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const timeoutRef = useRef<number | null>(null);
  const currentIndex = useRef(0);

  useEffect(() => {
    if (!enabled || !text) {
      const t = setTimeout(() => {
        setDisplayedText(text || "");
        setIsTyping(false);
      }, 0);
      // Reset index if completely disabled or empty
      if (!text) {
        currentIndex.current = 0;
      }
      return () => clearTimeout(t);
    }

    setTimeout(() => {
      setIsTyping(true);
    }, 0);

    const typeCharacter = () => {
      if (currentIndex.current < text.length) {
        setDisplayedText(text.slice(0, currentIndex.current + 1));
        currentIndex.current++;
        const nextSpeed = Math.floor(Math.random() * (maxSpeedMs - minSpeedMs + 1) + minSpeedMs);
        timeoutRef.current = window.setTimeout(typeCharacter, nextSpeed);
      } else {
        setIsTyping(false);
      }
    };

    // If we haven't reached the end of the text, start/continue typing
    if (currentIndex.current < text.length) {
      if (timeoutRef.current !== null) {
        window.clearTimeout(timeoutRef.current);
      }
      typeCharacter();
    } else {
      setIsTyping(false);
      setDisplayedText(text);
    }

    return () => {
      if (timeoutRef.current !== null) {
        window.clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [text, enabled, minSpeedMs, maxSpeedMs]);

  // Reset when text completely changes (not just appended) or when component unmounts
  useEffect(() => {
    if (enabled && text && !text.startsWith(displayedText)) {
      currentIndex.current = 0;
      const t = setTimeout(() => {
        setDisplayedText("");
      }, 0);
      return () => clearTimeout(t);
    }
  }, [text, enabled, displayedText]);

  return { displayedText, isTyping };
}
