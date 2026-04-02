"use client";

import { useState } from "react";
import { useComments, useCreateComment } from "@/hooks/useComments";
import CommentItem from "./CommentItem";
import { useAuth } from "@/context/AuthContext";

interface Props {
  postId: string;
}

export default function CommentSection({ postId }: Props) {
  const { user } = useAuth();
  const { data: comments } = useComments(postId, true);
  const createComment = useCreateComment(postId);
  const [text, setText] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    await createComment.mutateAsync(text);
    setText("");
  }

  return (
    <div className="_feed_inner_timeline_cooment_area">
      <div className="_feed_inner_comment_box">
        <form className="_feed_inner_comment_box_form" onSubmit={handleSubmit}>
          <div className="_feed_inner_comment_box_content">
            <div className="_feed_inner_comment_box_content_image">
              <img
                src={user?.avatar_url || "/assets/images/comment_img.png"}
                alt=""
                className="_comment_img"
              />
            </div>
            <div className="_feed_inner_comment_box_content_txt">
              <textarea
                className="form-control _comment_textarea"
                placeholder="Write a comment"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </div>
          </div>
          <div className="_feed_inner_comment_box_icon">
            <button type="submit" className="_feed_inner_comment_box_icon_btn" disabled={createComment.isPending}>
              Post
            </button>
          </div>
        </form>
      </div>
      <div className="_timline_comment_main">
        {comments?.map((c) => <CommentItem key={c.id} comment={c} />)}
      </div>
    </div>
  );
}
