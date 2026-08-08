export const queryKeys = {
  auth: {
    all: ["auth"] as const,
    me: () => [...queryKeys.auth.all, "me"] as const,
  },
  student: {
    all: ["student"] as const,
    dashboard: () => [...queryKeys.student.all, "dashboard"] as const,
    attendance: () => [...queryKeys.student.all, "attendance"] as const,
  },
  attendance: {
    all: ["attendance"] as const,
    activeSessions: () => [...queryKeys.attendance.all, "sessions", "active"] as const,
    session: (sessionId: string) =>
      [...queryKeys.attendance.all, "session", sessionId] as const,
    sessionStudents: (sessionId: string) =>
      [...queryKeys.attendance.session(sessionId), "students"] as const,
  },
};
