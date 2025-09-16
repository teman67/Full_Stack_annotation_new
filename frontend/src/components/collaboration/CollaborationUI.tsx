"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useCollaboration } from "@/contexts/CollaborationContext";

interface CollaborativeCursor {
  userId: string;
  userName: string;
  userColor: string;
  x: number;
  y: number;
  selection?: {
    start: number;
    end: number;
  };
}

interface CollaborationUIProps {
  documentId: string;
}

export function CollaborationUI({}: CollaborationUIProps) {
  const { connectedUsers, currentUser } = useCollaboration();
  const [cursors, setCursors] = useState<CollaborativeCursor[]>([]);

  useEffect(() => {
    // Update cursors when users change
    const newCursors = connectedUsers
      .filter((user) => user.cursor && user.id !== currentUser?.id)
      .map((user) => ({
        userId: user.id,
        userName: user.name,
        userColor: user.color,
        x: user.cursor!.x,
        y: user.cursor!.y,
        selection: user.cursor!.selection,
      }));
    setCursors(newCursors);
  }, [connectedUsers, currentUser]);

  if (!currentUser) return null;

  return (
    <>
      {/* User Presence Indicators */}
      <div className="fixed top-20 right-4 z-50 flex flex-col space-y-2">
        <div className="bg-white/90 backdrop-blur-sm border rounded-lg p-3 shadow-lg">
          <div className="text-xs font-medium text-muted-foreground mb-2">
            Active Users ({connectedUsers.length + 1})
          </div>

          {/* Current User */}
          <div className="flex items-center space-x-2 mb-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: currentUser.color }}
            />
            <div className="text-sm font-medium">{currentUser.name} (You)</div>
          </div>

          {/* Other Users */}
          {connectedUsers.map((user) => (
            <div key={user.id} className="flex items-center space-x-2 mb-1">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: user.color }}
              />
              <div className="text-sm">{user.name}</div>
              {user.cursor && (
                <Badge variant="outline" className="text-xs">
                  Active
                </Badge>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Collaborative Cursors */}
      {cursors.map((cursor) => (
        <CollaborativeCursorComponent key={cursor.userId} cursor={cursor} />
      ))}
    </>
  );
}

interface CollaborativeCursorComponentProps {
  cursor: CollaborativeCursor;
}

function CollaborativeCursorComponent({
  cursor,
}: CollaborativeCursorComponentProps) {
  return (
    <div
      className="fixed pointer-events-none z-40 transition-all duration-150"
      style={{
        left: cursor.x,
        top: cursor.y,
      }}
    >
      {/* Cursor Pointer */}
      <div className="relative" style={{ color: cursor.userColor }}>
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          className="drop-shadow-sm"
        >
          <path
            d="M2 2L18 7L11 9L9 16L2 2Z"
            fill="currentColor"
            stroke="white"
            strokeWidth="1"
          />
        </svg>

        {/* User Name Label */}
        <div
          className="absolute top-5 left-2 px-2 py-1 text-xs font-medium text-white rounded whitespace-nowrap"
          style={{ backgroundColor: cursor.userColor }}
        >
          {cursor.userName}
        </div>
      </div>

      {/* Text Selection Highlight */}
      {cursor.selection && (
        <div
          className="absolute opacity-30 rounded"
          style={{
            backgroundColor: cursor.userColor,
            left: -10,
            top: 20,
            width: 100,
            height: 20,
          }}
        />
      )}
    </div>
  );
}

// Hook for tracking mouse position and sending cursor updates
export function useCursorTracking(elementRef: React.RefObject<HTMLElement>) {
  const { sendCursorUpdate, currentUser } = useCollaboration();

  useEffect(() => {
    if (!elementRef.current || !currentUser) return;

    const element = elementRef.current;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = element.getBoundingClientRect();
      const x = e.clientX;
      const y = e.clientY;

      // Only send updates if cursor is within the element
      if (
        x >= rect.left &&
        x <= rect.right &&
        y >= rect.top &&
        y <= rect.bottom
      ) {
        sendCursorUpdate({ x, y });
      }
    };

    const handleMouseLeave = () => {
      // Hide cursor when mouse leaves the element
      sendCursorUpdate({ x: -1000, y: -1000 });
    };

    element.addEventListener("mousemove", handleMouseMove);
    element.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      element.removeEventListener("mousemove", handleMouseMove);
      element.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, [elementRef, sendCursorUpdate, currentUser]);
}

// Component for displaying real-time annotation updates
export function CollaborationNotifications() {
  const [notifications, setNotifications] = useState<
    Array<{
      id: string;
      message: string;
      user: string;
      timestamp: Date;
      type: "annotation" | "user";
    }>
  >([]);

  const { onAnnotationUpdate, onUserJoined, onUserLeft } = useCollaboration();

  useEffect(() => {
    onAnnotationUpdate((update) => {
      const message = `${
        update.action === "create"
          ? "added"
          : update.action === "update"
          ? "updated"
          : "deleted"
      } an annotation`;

      setNotifications((prev) => [
        {
          id: Date.now().toString(),
          message,
          user: "User", // In real implementation, this would come from the update
          timestamp: new Date(),
          type: "annotation",
        },
        ...prev.slice(0, 4), // Keep only last 5 notifications
      ]);

      // Auto-remove notification after 5 seconds
      setTimeout(() => {
        setNotifications((prev) => prev.slice(0, -1));
      }, 5000);
    });

    onUserJoined((user) => {
      setNotifications((prev) => [
        {
          id: Date.now().toString(),
          message: "joined the document",
          user: user.name,
          timestamp: new Date(),
          type: "user",
        },
        ...prev.slice(0, 4),
      ]);
    });

    onUserLeft(() => {
      setNotifications((prev) => [
        {
          id: Date.now().toString(),
          message: "left the document",
          user: "User", // In real implementation, we'd track user names
          timestamp: new Date(),
          type: "user",
        },
        ...prev.slice(0, 4),
      ]);
    });
  }, [onAnnotationUpdate, onUserJoined, onUserLeft]);

  if (notifications.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className="bg-white/90 backdrop-blur-sm border rounded-lg p-3 shadow-lg max-w-sm animate-in slide-in-from-right"
        >
          <div className="flex items-center space-x-2">
            <Avatar className="h-6 w-6">
              <AvatarFallback className="text-xs">
                {notification.user.charAt(0)}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 text-sm">
              <span className="font-medium">{notification.user}</span>
              <span className="text-muted-foreground">
                {" "}
                {notification.message}
              </span>
            </div>
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {notification.timestamp.toLocaleTimeString()}
          </div>
        </div>
      ))}
    </div>
  );
}
