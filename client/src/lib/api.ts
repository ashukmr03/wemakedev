// API base URL — set VITE_API_URL in Vercel environment variables to point at
// the Render backend. Falls back to empty string (same-origin) for local dev
// when the Vite proxy in vite.config.ts is handling /api/* requests.
const API_BASE = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.NEXT_PUBLIC_API_URL ||
  ""
).replace(/\/$/, "");

// ---------------------------------------------------------------------------
// Types expected by the frontend UI
// ---------------------------------------------------------------------------
export interface Task {
  id: string;
  title: string;
  assignee: string;
  initials: string;
  due: string;
  status: "pending" | "completed";
  tone: string;
}

export interface TimelineEvent {
  id: string;
  type: string;
  title: string;
  description: string;
  author: string;
  time: string;
  review?: boolean;
}

export interface DashboardData {
  senior: { name: string; age: number; relation: string; status?: string };
  progress: { completed: number; total: number };
  summary: string;
  tasks: Task[];
  timeline: TimelineEvent[];
  appointments: {
    id: string;
    title: string;
    doctor: string;
    location: string;
    date: string;
    time: string;
  }[];
  notifications: {
    id: string;
    title: string;
    body: string;
    time: string;
    unread: boolean;
  }[];
}

// ---------------------------------------------------------------------------
// Mock / fallback data used when the backend is unreachable
// ---------------------------------------------------------------------------
export const mockDashboard: DashboardData = {
  senior: { name: "Lakshmi Rao", age: 72, relation: "Meera's mother", status: "steady" },
  progress: { completed: 2, total: 4 },
  summary:
    "Lakshmi is having a steady day. Her morning medicine is complete, and the family has two check-ins planned. One update about knee stiffness is waiting for a human review.",
  tasks: [
    {
      id: "t1",
      title: "Morning medicine",
      assignee: "Meera",
      initials: "MR",
      due: "Completed at 8:15 AM",
      status: "completed",
      tone: "mint",
    },
    {
      id: "t2",
      title: "Collect blood report",
      assignee: "Arun",
      initials: "AR",
      due: "Friday",
      status: "pending",
      tone: "lavender",
    },
    {
      id: "t3",
      title: "Evening check-in",
      assignee: "Ravi",
      initials: "RR",
      due: "Today · 7:00 PM",
      status: "pending",
      tone: "peach",
    },
    {
      id: "t4",
      title: "Refill prescription",
      assignee: "Meera",
      initials: "MR",
      due: "Tomorrow",
      status: "pending",
      tone: "mint",
    },
  ],
  timeline: [
    {
      id: "e1",
      type: "update",
      title: "Knee pain update",
      description: "Lakshmi mentioned her knee felt stiff after the morning walk.",
      author: "Meera",
      time: "Today · 9:42 AM",
      review: true,
    },
    {
      id: "e2",
      type: "task",
      title: "Morning medicine completed",
      description: "Marked complete by Meera.",
      author: "Meera",
      time: "Today · 8:15 AM",
    },
    {
      id: "e3",
      type: "appointment",
      title: "Doctor appointment added",
      description: "Dr. Anita Menon · Tomorrow at 10:00 AM.",
      author: "Ravi",
      time: "Yesterday · 6:20 PM",
    },
  ],
  appointments: [
    {
      id: "a1",
      title: "Doctor appointment",
      doctor: "Dr. Anita Menon",
      location: "Apollo Clinic · Room 204",
      date: "Tomorrow",
      time: "10:00 AM",
    },
  ],
  notifications: [
    {
      id: "n1",
      title: "Review needed",
      body: "Meera's knee pain update is ready for a human review.",
      time: "12 min ago",
      unread: true,
    },
    {
      id: "n2",
      title: "Arun joined the circle",
      body: "Your family care team is growing.",
      time: "Yesterday",
      unread: false,
    },
  ],
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
/** Extract the `data` field from the backend's { success, data, meta } envelope. */
function unwrap<T>(json: Record<string, unknown>): T {
  return (json.data ?? json) as T;
}

/** Simple initials from a full name like "Meera Rao" -> "MR" */
function initialsOf(name: string): string {
  return name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

// ---------------------------------------------------------------------------
// Backend → Frontend mappers
// ---------------------------------------------------------------------------
function mapTask(raw: Record<string, unknown>, idx: number): Task {
  const assignedTo =
    (raw.assignedTo as string) || (raw.assigned_to as string) || "";
  const dueAt = (raw.dueAt as string) || (raw.due_at as string) || "";
  const status =
    (raw.status as string) === "completed" ? "completed" : "pending";
  const tones = ["mint", "lavender", "peach"];
  return {
    id: (raw.id as string) || `t-${idx}`,
    title: (raw.title as string) || "Care Task",
    assignee: assignedTo,
    initials: initialsOf(assignedTo || "Family"),
    due: dueAt,
    status,
    tone: tones[idx % 3],
  };
}

function mapTimelineEvent(raw: Record<string, unknown>, idx: number): TimelineEvent {
  const createdAt = (raw.createdAt as string) || (raw.created_at as string) || "";
  const timeLabel = createdAt
    ? new Date(createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "Today";
  return {
    id: (raw.id as string) || `e-${idx}`,
    type: (raw.type as string) || "update",
    title:
      (raw.title as string) ||
      ((raw.description as string) || "").split(".")[0] ||
      "Care Update",
    description: (raw.description as string) || "",
    author:
      (raw.recordedBy as string) || (raw.recorded_by as string) || "Family",
    time: timeLabel,
    review:
      (raw.needsHumanReview as boolean) ??
      (raw.needs_human_review as boolean) ??
      false,
  };
}

function mapAppointment(raw: Record<string, unknown>, idx: number) {
  const scheduledAt =
    (raw.scheduledAt as string) || (raw.scheduled_at as string) || "";
  const datePart = scheduledAt
    ? new Date(scheduledAt).toLocaleDateString([], {
        month: "short",
        day: "numeric",
      })
    : (raw.date as string) || "TBD";
  const timePart = scheduledAt
    ? new Date(scheduledAt).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    : (raw.time as string) || "TBD";
  return {
    id: (raw.id as string) || `a-${idx}`,
    title: (raw.title as string) || "Appointment",
    doctor:
      (raw.doctorName as string) || (raw.doctor_name as string) || "Doctor",
    location: (raw.location as string) || "",
    date: datePart,
    time: timePart,
  };
}

function mapNotification(raw: Record<string, unknown>, idx: number) {
  const createdAt =
    (raw.createdAt as string) || (raw.created_at as string) || "";
  return {
    id: (raw.id as string) || `n-${idx}`,
    title: (raw.title as string) || "Notification",
    body: (raw.message as string) || (raw.body as string) || "",
    time: createdAt ? new Date(createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "Recently",
    unread: !(raw.read as boolean),
  };
}

// ---------------------------------------------------------------------------
// API functions — each returns frontend-shaped data with mock fallback
// ---------------------------------------------------------------------------
export async function getDashboard(): Promise<DashboardData> {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    const raw = unwrap<Record<string, unknown>>(json);

    const senior = (raw.senior as Record<string, unknown>) || {};
    const tp = (raw.todayProgress as Record<string, unknown>) || {};
    const pendingTasks = ((raw.pendingTasks as unknown[]) || []) as Record<string, unknown>[];
    const recentCareEvents = ((raw.recentCareEvents as unknown[]) || []) as Record<string, unknown>[];
    const upcomingAppointments = ((raw.upcomingAppointments as unknown[]) || []) as Record<string, unknown>[];
    const rawNotifs = ((raw.notifications as unknown[]) || []) as Record<string, unknown>[];
    const dailySummary = (raw.dailySummary as Record<string, unknown>) || {};

    return {
      senior: {
        name: (senior.name as string) || mockDashboard.senior.name,
        age: (senior.age as number) || mockDashboard.senior.age,
        relation: "Mother",
        status: "steady",
      },
      progress: {
        completed: (tp.completedTasks as number) || 0,
        total: (tp.totalTasks as number) || 0,
      },
      summary: (dailySummary.summary as string) || mockDashboard.summary,
      tasks: pendingTasks.map(mapTask),
      timeline: recentCareEvents.map(mapTimelineEvent),
      appointments: upcomingAppointments.map(mapAppointment),
      notifications: rawNotifs.map(mapNotification),
    };
  } catch {
    return mockDashboard;
  }
}

export async function getTasks(): Promise<Task[]> {
  try {
    const res = await fetch(`${API_BASE}/api/tasks`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    const raw = unwrap<Record<string, unknown>[]>(json);
    return Array.isArray(raw) ? raw.map(mapTask) : mockDashboard.tasks;
  } catch {
    return mockDashboard.tasks;
  }
}

export async function getTimeline(): Promise<TimelineEvent[]> {
  try {
    const res = await fetch(`${API_BASE}/api/care/timeline`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    const raw = unwrap<Record<string, unknown>[]>(json);
    return Array.isArray(raw)
      ? raw.map(mapTimelineEvent)
      : mockDashboard.timeline;
  } catch {
    return mockDashboard.timeline;
  }
}

export async function getAppointments(): Promise<DashboardData["appointments"]> {
  try {
    const res = await fetch(`${API_BASE}/api/appointments`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    const raw = unwrap<Record<string, unknown>[]>(json);
    return Array.isArray(raw)
      ? raw.map(mapAppointment)
      : mockDashboard.appointments;
  } catch {
    return mockDashboard.appointments;
  }
}

export async function getFamily(): Promise<
  { name: string; role: string; initials: string }[]
> {
  try {
    const res = await fetch(`${API_BASE}/api/family/demo-family`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    const raw = unwrap<Record<string, unknown>>(json);
    const members = ((raw.members as unknown[]) || []) as Record<
      string,
      unknown
    >[];
    return members.map((m) => ({
      name: (m.name as string) || "Unknown",
      role: `${(m.relationship as string) || ""} · ${(m.role as string) || ""}`,
      initials: initialsOf((m.name as string) || "Unknown"),
    }));
  } catch {
    return [
      { name: "Lakshmi Rao", role: "Senior", initials: "LR" },
      { name: "Meera Rao", role: "Daughter · Caregiver", initials: "MR" },
      { name: "Arun Rao", role: "Son · Caregiver", initials: "AR" },
      { name: "Ravi Rao", role: "Coordinator", initials: "RR" },
    ];
  }
}

export async function getNotifications(): Promise<DashboardData["notifications"]> {
  try {
    const res = await fetch(`${API_BASE}/api/notifications`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    const raw = unwrap<Record<string, unknown>[]>(json);
    return Array.isArray(raw)
      ? raw.map(mapNotification)
      : mockDashboard.notifications;
  } catch {
    return mockDashboard.notifications;
  }
}

export async function extractCareUpdate(
  text: string,
  familyId = "demo-family"
): Promise<unknown> {
  try {
    const res = await fetch(`${API_BASE}/api/ai/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, family_id: familyId }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return unwrap(json);
  } catch {
    return { text };
  }
}

export async function confirmCareUpdate(payload: {
  text: string;
  familyId: string;
}): Promise<unknown> {
  try {
    const res = await fetch(`${API_BASE}/api/care/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        family_id: payload.familyId,
        senior_id: "lakshmi-rao",
        original_text: payload.text,
        confirmed_by: "meera-rao",
        extraction: {},
      }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return unwrap(json);
  } catch {
    return { success: true };
  }
}

export async function completeTask(id: string): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/api/tasks/${id}/complete`, {
      method: "PATCH",
      headers: { "X-Demo-User": "meera-rao" },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  } catch {
    // Silently fail — local state is already updated in the UI.
  }
}

export async function markNotificationRead(id: string): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/api/notifications/${id}/read`, {
      method: "PATCH",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  } catch {
    // Silently fail.
  }
}
