"use client";

import { useState } from "react";
import api from "@/lib/api";
import { Comment } from "@/types";
import WhoLikedModal from "./WhoLikedModal";
import ReplyItem from "./ReplyItem";
import { useReplies, useCreateReply } from "@/hooks/useReplies";

interface Props {
  comment: Comment;
}

export default function CommentItem({ comment }: Props) {
  const [showLikedModal, setShowLikedModal] = useState(false);
  const [liked, setLiked] = useState(comment.liked_by_me);
  const [likeCount, setLikeCount] = useState(comment.like_count);
  const [showReplies, setShowReplies] = useState(false);
  const [replyText, setReplyText] = useState("");

  const { data: replies } = useReplies(comment.id, showReplies);
  const createReply = useCreateReply(comment.id);

  async function toggleLike() {
    const prev = liked;
    setLiked(!prev);
    setLikeCount((c) => c + (prev ? -1 : 1));
    try {
      if (prev) {
        const res = await api.delete<{ like_count: number }>(`/api/likes/comment/${comment.id}`);
        setLikeCount(res.data.like_count);
      } else {
        const res = await api.post<{ like_count: number }>(`/api/likes/comment/${comment.id}`);
        setLikeCount(res.data.like_count);
      }
    } catch {
      setLiked(prev);
      setLikeCount((c) => c + (prev ? 1 : -1));
    }
  }

  async function submitReply(e: React.FormEvent) {
    e.preventDefault();
    if (!replyText.trim()) return;
    await createReply.mutateAsync(replyText);
    setReplyText("");
  }

  return (
    <div className="_comment_main">
      <div className="_comment_image">
        <img
          src={comment.author.avatar_url || "/assets/images/profile.png"}
          alt={comment.author.first_name}
          className="_comment_img1"
        />
      </div>
      <div className="_comment_area">
        <div className="_comment_details">
          <div className="_comment_details_top">
            <div className="_comment_name">
              <h4 className="_comment_name_title">{comment.author.first_name} {comment.author.last_name}</h4>
            </div>
          </div>
          <div className="_comment_status">
            <p className="_comment_status_text"><span>{comment.content}</span></p>
          </div>
          <div className="_total_reactions">
            <div className="_total_react">
              <span
                className="_reaction_like"
                onClick={toggleLike}
                style={{ cursor: "pointer" }}
                title="Like"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill={liked ? "#1877f2" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
              </span>
              <span
                className="_reaction_heart"
                onClick={() => likeCount > 0 && setShowLikedModal(true)}
                style={{ cursor: likeCount > 0 ? "pointer" : "default" }}
                title="See who liked"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill={liked ? "#e0245e" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
              </span>
            </div>
            <span className="_total">{likeCount > 0 ? likeCount : ""}</span>
          </div>
          <div className="_comment_reply">
            <div className="_comment_reply_num">
              <ul className="_comment_reply_list">
                <li><span style={{ cursor: "pointer" }} onClick={toggleLike}>Like.</span></li>
                <li>
                  <span style={{ cursor: "pointer" }} onClick={() => setShowReplies((v) => !v)}>
                    Reply.
                  </span>
                </li>
                <li><span className="_time_link">.{new Date(comment.created_at).toLocaleDateString()}</span></li>
              </ul>
            </div>
          </div>
        </div>

        {showReplies && (
          <>
            <div className="_feed_inner_comment_box">
              <form className="_feed_inner_comment_box_form" onSubmit={submitReply}>
                <div className="_feed_inner_comment_box_content">
                  <div className="_feed_inner_comment_box_content_txt">
                    <textarea
                      className="form-control _comment_textarea"
                      placeholder="Write a reply"
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                    />
                  </div>
                </div>
                <div className="_feed_inner_comment_box_icon">
                  <button type="submit" className="_feed_inner_comment_box_icon_btn">Reply</button>
                </div>
              </form>
            </div>
            {replies?.map((r) => (
              <ReplyItem key={r.id} reply={r} onReplyLikeChange={() => {}} />
            ))}
          </>
        )}
      </div>
      {showLikedModal && (
        <WhoLikedModal targetType="comment" targetId={comment.id} onClose={() => setShowLikedModal(false)} />
      )}
    </div>
  );
}
