"use client";

import { useState } from "react";
import api from "@/lib/api";
import { Reply } from "@/types";
import WhoLikedModal from "./WhoLikedModal";

interface Props {
  reply: Reply;
  onReplyLikeChange: (replyId: string, delta: number, liked: boolean) => void;
}

export default function ReplyItem({ reply, onReplyLikeChange }: Props) {
  const [showLikedModal, setShowLikedModal] = useState(false);
  const [liked, setLiked] = useState(reply.liked_by_me);
  const [likeCount, setLikeCount] = useState(reply.like_count);

  async function toggleLike() {
    try {
      if (liked) {
        const res = await api.delete<{ like_count: number }>(`/api/likes/reply/${reply.id}`);
        setLiked(false);
        setLikeCount(res.data.like_count);
      } else {
        const res = await api.post<{ like_count: number }>(`/api/likes/reply/${reply.id}`);
        setLiked(true);
        setLikeCount(res.data.like_count);
      }
    } catch {}
  }

  return (
    <div className="_comment_main" style={{ marginLeft: 40 }}>
      <div className="_comment_image">
        <img
          src={reply.author.avatar_url || "/assets/images/profile.png"}
          alt={reply.author.first_name}
          className="_comment_img1"
        />
      </div>
      <div className="_comment_area">
        <div className="_comment_details">
          <div className="_comment_details_top">
            <div className="_comment_name">
              <h4 className="_comment_name_title">{reply.author.first_name} {reply.author.last_name}</h4>
            </div>
          </div>
          <div className="_comment_status">
            <p className="_comment_status_text"><span>{reply.content}</span></p>
          </div>
          <div className="_total_reactions">
            <div className="_total_react">
              <span
                className="_reaction_like"
                onClick={() => setShowLikedModal(true)}
                style={{ cursor: "pointer" }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill={liked ? "#1877f2" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
              </span>
            </div>
            <span className="_total">{likeCount}</span>
          </div>
          <div className="_comment_reply">
            <div className="_comment_reply_num">
              <ul className="_comment_reply_list">
                <li><span style={{ cursor: "pointer" }} onClick={toggleLike}>Like.</span></li>
                <li><span className="_time_link">.{new Date(reply.created_at).toLocaleDateString()}</span></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      {showLikedModal && (
        <WhoLikedModal targetType="reply" targetId={reply.id} onClose={() => setShowLikedModal(false)} />
      )}
    </div>
  );
}
