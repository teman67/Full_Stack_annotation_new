"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useRef,
} from "react";

interface Socket {
  connected: boolean;
  emit: (event: string, data: unknown) => void;
  on: (event: string, callback: (...args: unknown[]) => void) => void;
  off: (event: string, callback?: (...args: unknown[]) => void) => void;
  disconnect: () => void;
}

interface CollaborationUser {
  id: string;
  name: string;
  avatar?: string;
  color: string;
  cursor?: {
    x: number;
    y: number;
    selection?: {
      start: number;
      end: number;
    };
  };
}

interface AnnotationUpdate {
  id: string;
  documentId: string;
  action: "create" | "update" | "delete";
  annotation?: {
    id: string;
    text: string;
    start: number;
    end: number;
    tagId: number;
    tagName: string;
    tagColor: string;
    userId: string;
    userName: string;
  };
  userId: string;
  timestamp: string;
}

interface CollaborationContextType {
  socket: Socket | null;
  isConnected: boolean;
  connectedUsers: CollaborationUser[];
  currentUser: CollaborationUser | null;
  joinDocument: (documentId: string, userId: string, userName: string) => void;
  leaveDocument: () => void;
  sendAnnotationUpdate: (update: AnnotationUpdate) => void;
  sendCursorUpdate: (position: {
    x: number;
    y: number;
    selection?: { start: number; end: number };
  }) => void;
  onAnnotationUpdate: (callback: (update: AnnotationUpdate) => void) => void;
  onUserJoined: (callback: (user: CollaborationUser) => void) => void;
  onUserLeft: (callback: (userId: string) => void) => void;
  onCursorUpdate: (
    callback: (
      userId: string,
      cursor: {
        x: number;
        y: number;
        selection?: { start: number; end: number };
      }
    ) => void
  ) => void;
}

const CollaborationContext = createContext<CollaborationContextType | null>(
  null
);

const USER_COLORS = [
  "#3B82F6", // blue
  "#EF4444", // red
  "#10B981", // green
  "#F59E0B", // yellow
  "#8B5CF6", // purple
  "#F97316", // orange
  "#EC4899", // pink
  "#06B6D4", // cyan
];

interface CollaborationProviderProps {
  children: React.ReactNode;
}

export function CollaborationProvider({
  children,
}: CollaborationProviderProps) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectedUsers, setConnectedUsers] = useState<CollaborationUser[]>([]);
  const [currentUser, setCurrentUser] = useState<CollaborationUser | null>(
    null
  );
  const [currentDocumentId, setCurrentDocumentId] = useState<string | null>(
    null
  );

  const annotationUpdateCallbackRef = useRef<
    ((update: AnnotationUpdate) => void) | null
  >(null);
  const userJoinedCallbackRef = useRef<
    ((user: CollaborationUser) => void) | null
  >(null);
  const userLeftCallbackRef = useRef<((userId: string) => void) | null>(null);
  const cursorUpdateCallbackRef = useRef<
    | ((
        userId: string,
        cursor: {
          x: number;
          y: number;
          selection?: { start: number; end: number };
        }
      ) => void)
    | null
  >(null);

  useEffect(() => {
    // Initialize socket connection (mock for development)
    // In production, this would connect to your WebSocket server
    const mockSocket: Socket = {
      connected: true,
      emit: (event: string, data: unknown) => {
        console.log("Mock socket emit:", event, data);
      },
      on: (event: string) => {
        console.log("Mock socket listener registered:", event);
        // Store callbacks for mock events
      },
      off: (event: string) => {
        console.log("Mock socket listener removed:", event);
      },
      disconnect: () => {
        console.log("Mock socket disconnected");
      },
    };

    setSocket(mockSocket);
    setIsConnected(true);

    return () => {
      if (mockSocket) {
        mockSocket.disconnect();
      }
    };
  }, []);

  const joinDocument = (
    documentId: string,
    userId: string,
    userName: string
  ) => {
    if (!socket) return;

    const userColor =
      USER_COLORS[Math.floor(Math.random() * USER_COLORS.length)];
    const user: CollaborationUser = {
      id: userId,
      name: userName,
      color: userColor,
    };

    setCurrentUser(user);
    setCurrentDocumentId(documentId);

    // Mock joining document
    socket.emit("join-document", { documentId, user });

    // Simulate other users already in the document
    setTimeout(() => {
      const mockUsers: CollaborationUser[] = [
        {
          id: "user-2",
          name: "Dr. Sarah Wilson",
          color: "#EF4444",
          cursor: { x: 100, y: 200 },
        },
        {
          id: "user-3",
          name: "Prof. Michael Chen",
          color: "#10B981",
          cursor: { x: 300, y: 150 },
        },
      ];
      setConnectedUsers(mockUsers);
    }, 1000);
  };

  const leaveDocument = () => {
    if (!socket || !currentDocumentId) return;

    socket.emit("leave-document", { documentId: currentDocumentId });
    setCurrentDocumentId(null);
    setCurrentUser(null);
    setConnectedUsers([]);
  };

  const sendAnnotationUpdate = (update: AnnotationUpdate) => {
    if (!socket || !currentDocumentId) return;

    socket.emit("annotation-update", update);

    // Mock receiving the update for demonstration
    setTimeout(() => {
      if (annotationUpdateCallbackRef.current) {
        annotationUpdateCallbackRef.current(update);
      }
    }, 100);
  };

  const sendCursorUpdate = (position: {
    x: number;
    y: number;
    selection?: { start: number; end: number };
  }) => {
    if (!socket || !currentDocumentId || !currentUser) return;

    socket.emit("cursor-update", {
      documentId: currentDocumentId,
      userId: currentUser.id,
      cursor: position,
    });
  };

  const onAnnotationUpdate = (callback: (update: AnnotationUpdate) => void) => {
    annotationUpdateCallbackRef.current = callback;
  };

  const onUserJoined = (callback: (user: CollaborationUser) => void) => {
    userJoinedCallbackRef.current = callback;
  };

  const onUserLeft = (callback: (userId: string) => void) => {
    userLeftCallbackRef.current = callback;
  };

  const onCursorUpdate = (
    callback: (
      userId: string,
      cursor: {
        x: number;
        y: number;
        selection?: { start: number; end: number };
      }
    ) => void
  ) => {
    cursorUpdateCallbackRef.current = callback;
  };

  const value: CollaborationContextType = {
    socket,
    isConnected,
    connectedUsers,
    currentUser,
    joinDocument,
    leaveDocument,
    sendAnnotationUpdate,
    sendCursorUpdate,
    onAnnotationUpdate,
    onUserJoined,
    onUserLeft,
    onCursorUpdate,
  };

  return (
    <CollaborationContext.Provider value={value}>
      {children}
    </CollaborationContext.Provider>
  );
}

export function useCollaboration() {
  const context = useContext(CollaborationContext);
  if (!context) {
    throw new Error(
      "useCollaboration must be used within a CollaborationProvider"
    );
  }
  return context;
}

// Hook for document-specific collaboration
export function useDocumentCollaboration(
  documentId: string,
  userId: string,
  userName: string
) {
  const collaboration = useCollaboration();

  useEffect(() => {
    if (documentId && userId && userName) {
      collaboration.joinDocument(documentId, userId, userName);
    }

    return () => {
      collaboration.leaveDocument();
    };
  }, [documentId, userId, userName, collaboration]);

  return collaboration;
}
