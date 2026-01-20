"use client";

import { useEffect, useCallback, useState, useRef } from "react";
import { createPortal } from "react-dom";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  size?: "sm" | "md" | "lg" | "xl";
}

export function Modal({ isOpen, onClose, children, title, size = "md" }: ModalProps) {
  const [keyboardVisible, setKeyboardVisible] = useState(false);
  const [viewportHeight, setViewportHeight] = useState<number | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  const handleEscape = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose]
  );

  // Handle visual viewport changes (keyboard open/close)
  useEffect(() => {
    if (!isOpen) return;

    const viewport = window.visualViewport;
    if (!viewport) return;

    const handleViewportResize = () => {
      const windowHeight = window.innerHeight;
      const currentViewportHeight = viewport.height;

      // If viewport height is significantly less than window height, keyboard is likely open
      const isKeyboardOpen = windowHeight - currentViewportHeight > 150;
      setKeyboardVisible(isKeyboardOpen);
      setViewportHeight(currentViewportHeight);
    };

    // Initial check
    handleViewportResize();

    viewport.addEventListener("resize", handleViewportResize);
    viewport.addEventListener("scroll", handleViewportResize);

    return () => {
      viewport.removeEventListener("resize", handleViewportResize);
      viewport.removeEventListener("scroll", handleViewportResize);
    };
  }, [isOpen]);

  // Scroll focused input into view when keyboard opens
  useEffect(() => {
    if (!isOpen || !keyboardVisible) return;

    const handleFocusIn = () => {
      // Small delay to let keyboard fully open
      setTimeout(() => {
        const activeElement = document.activeElement as HTMLElement;
        if (activeElement && modalRef.current?.contains(activeElement)) {
          activeElement.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }, 100);
    };

    document.addEventListener("focusin", handleFocusIn);
    return () => document.removeEventListener("focusin", handleFocusIn);
  }, [isOpen, keyboardVisible]);

  useEffect(() => {
    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, handleEscape]);

  if (!isOpen) return null;

  const sizeClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
  };

  // Calculate max height based on viewport
  const maxHeightStyle = viewportHeight
    ? { maxHeight: `${viewportHeight - 32}px` }
    : { maxHeight: "calc(100vh - 2rem)" };

  return createPortal(
    <div
      className={`fixed inset-0 z-50 flex ${
        keyboardVisible ? "items-start pt-4" : "items-center"
      } justify-center overflow-y-auto`}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      {/* Modal */}
      <div
        ref={modalRef}
        style={maxHeightStyle}
        className={`relative w-full ${sizeClasses[size]} mx-4 animate-modal-enter rounded-xl bg-white dark:bg-gray-800 p-6 shadow-2xl overflow-y-auto`}
      >
        {title && (
          <div className="mb-4 flex items-center justify-between sticky top-0 bg-white dark:bg-gray-800 -mt-6 -mx-6 px-6 pt-6 pb-4 z-10">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
            <button
              onClick={onClose}
              className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
        {children}
      </div>
    </div>,
    document.body
  );
}
