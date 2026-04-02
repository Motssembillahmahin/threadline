"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { LikedUser } from "@/types";

interface Props {
  targetType: "post" | "comment" | "reply";
  targetId: string;
  onClose: () => void;
}

export default function WhoLikedModal({ targetType, targetId, onClose }: Props) {
  const [users, setUsers] = useState<LikedUser[]>([]);

  useEffect(() => {
    api.get<LikedUser[]>(`/api/likes/${targetType}/${targetId}/users`).then((r) => setUsers(r.data));
  }, [targetType, targetId]);

  return (
    <div
      style={{
        position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)",
        display: "flex", alignItems: "center", justifyContent: "center", zIndex: 9999,
      }}
      onClick={onClose}
    >
      <div
        style={{ background: "#fff", borderRadius: 8, padding: 24, minWidth: 300, maxHeight: 400, overflowY: "auto" }}
        onClick={(e) => e.stopPropagation()}
      >
        <h4 style={{ marginBottom: 16 }}>Liked by</h4>
        {users.length === 0 && <p>No likes yet.</p>}
        {users.map((u) => (
          <div key={u.id} style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
            <img
              src={u.avatar_url || "/assets/images/profile.png"}
              alt={u.first_name}
              style={{ width: 36, height: 36, borderRadius: "50%", objectFit: "cover" }}
            />
            <span>{u.first_name} {u.last_name}</span>
          </div>
        ))}
        <button type="button" onClick={onClose} style={{ marginTop: 8 }}>Close</button>
      </div>
    </div>
  );
}
