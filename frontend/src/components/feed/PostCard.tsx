"use client";

import { useState } from "react";
import api from "@/lib/api";
import { Post } from "@/types";
import { useAuth } from "@/context/AuthContext";
import { useDeletePost } from "@/hooks/usePosts";
import { useComments } from "@/hooks/useComments";
import CommentSection from "./CommentSection";
import CommentItem from "./CommentItem";
import WhoLikedModal from "./WhoLikedModal";

interface Props {
  post: Post;
}

export default function PostCard({ post }: Props) {
  const { user } = useAuth();
  const deletePost = useDeletePost();
  const [liked, setLiked] = useState(post.liked_by_me);
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [showComments, setShowComments] = useState(false);
  const [showLikedModal, setShowLikedModal] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const isOwner = user?.id === post.author.id;

  const { data: comments } = useComments(post.id, post.comment_count > 0);
  const latestComment = comments?.[comments.length - 1];
  const previousCount = post.comment_count - 1;

  function resolveImageUrl(url: string | null): string | null {
    if (!url) return null;
    // Cloudinary and any other absolute URLs are used directly
    if (url.startsWith("http")) return url;
    // Local / Docker: relative path like /static/uploads/xxx.jpg
    const base = process.env.NEXT_PUBLIC_MEDIA_URL?.replace("/static/uploads", "") || "http://localhost:8000";
    return `${base}${url}`;
  }

  async function toggleLike() {
    const prev = liked;
    setLiked(!prev);
    setLikeCount((c) => c + (prev ? -1 : 1));
    try {
      if (prev) {
        const res = await api.delete<{ like_count: number }>(`/api/likes/post/${post.id}`);
        setLikeCount(res.data.like_count);
      } else {
        const res = await api.post<{ like_count: number }>(`/api/likes/post/${post.id}`);
        setLikeCount(res.data.like_count);
      }
    } catch {
      setLiked(prev);
      setLikeCount((c) => c + (prev ? 1 : -1));
    }
  }

  function timeAgo(isoDate: string) {
    const diff = Date.now() - new Date(isoDate).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  }

  return (
    <div className="_feed_inner_timeline_post_area _b_radious6 _padd_b24 _padd_t24 _mar_b16">
      <div className="_feed_inner_timeline_content _padd_r24 _padd_l24">
        <div className="_feed_inner_timeline_post_top">
          <div className="_feed_inner_timeline_post_box">
            <div className="_feed_inner_timeline_post_box_image">
              <img
                src={post.author.avatar_url || "/assets/images/profile.png"}
                alt={post.author.first_name}
                className="_post_img"
              />
            </div>
            <div className="_feed_inner_timeline_post_box_txt">
              <h4 className="_feed_inner_timeline_post_box_title">
                {post.author.first_name} {post.author.last_name}
              </h4>
              <p className="_feed_inner_timeline_post_box_para">
                {timeAgo(post.created_at)} · <a href="#0">{post.visibility === "private" ? "Private" : "Public"}</a>
              </p>
            </div>
          </div>
          <div className="_feed_inner_timeline_post_box_dropdown">
            <div className="_feed_timeline_post_dropdown">
              <button
                className="_feed_timeline_post_dropdown_link"
                onClick={() => setDropdownOpen((v) => !v)}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="4" height="17" fill="none" viewBox="0 0 4 17">
                  <circle cx="2" cy="2" r="2" fill="#C4C4C4" />
                  <circle cx="2" cy="8" r="2" fill="#C4C4C4" />
                  <circle cx="2" cy="15" r="2" fill="#C4C4C4" />
                </svg>
              </button>
            </div>
            {dropdownOpen && (
              <div className="_feed_timeline_dropdown _timeline_dropdown" style={{ display: "block" }}>
                <ul className="_feed_timeline_dropdown_list">
                  {isOwner ? (
                    <>
                      <li className="_feed_timeline_dropdown_item">
                        <button
                          className="_feed_timeline_dropdown_link"
                          onClick={async () => {
                            if (confirm("Delete this post?")) {
                              await deletePost.mutateAsync(post.id);
                            }
                            setDropdownOpen(false);
                          }}
                          style={{ background: "none", border: "none", cursor: "pointer", width: "100%", textAlign: "left" }}
                        >
                          Delete Post
                        </button>
                      </li>
                    </>
                  ) : (
                    <li className="_feed_timeline_dropdown_item">
                      <a href="#0" className="_feed_timeline_dropdown_link">Save Post</a>
                    </li>
                  )}
                </ul>
              </div>
            )}
          </div>
        </div>
        {post.content && (
          <h4 className="_feed_inner_timeline_post_title">{post.content}</h4>
        )}
        {post.image_url && (
          <div className="_feed_inner_timeline_image">
            <img
              src={resolveImageUrl(post.image_url) ?? ""}
              alt="post"
              className="_time_img"
              style={{ maxWidth: "100%", borderRadius: 8 }}
            />
          </div>
        )}
      </div>
      <div className="_feed_inner_timeline_total_reacts _padd_r24 _padd_l24 _mar_b26">
        <div
          className="_feed_inner_timeline_total_reacts_image"
          style={{ cursor: likeCount > 0 ? "pointer" : "default" }}
          onClick={() => likeCount > 0 && setShowLikedModal(true)}
        >
          {likeCount > 0 && <img src="/assets/images/react_img1.png" alt="" className="_react_img1" />}
          {likeCount > 1 && <img src="/assets/images/react_img2.png" alt="" className="_react_img" />}
          {likeCount > 2 && <img src="/assets/images/react_img3.png" alt="" className="_react_img _rect_img_mbl_none" />}
          {likeCount > 3 && <img src="/assets/images/react_img4.png" alt="" className="_react_img _rect_img_mbl_none" />}
          {likeCount > 4 && <img src="/assets/images/react_img5.png" alt="" className="_react_img _rect_img_mbl_none" />}
          {likeCount > 5 && (
            <p className="_feed_inner_timeline_total_reacts_para">{likeCount - 5}+</p>
          )}
        </div>
        <div className="_feed_inner_timeline_total_reacts_txt">
          <p className="_feed_inner_timeline_total_reacts_para1">
            <a href="#0" onClick={(e) => { e.preventDefault(); setShowComments((v) => !v); }}>
              <span>{post.comment_count}</span> Comment
            </a>
          </p>
          <p className="_feed_inner_timeline_total_reacts_para2">
            <span>{likeCount}</span> Like{likeCount !== 1 ? "s" : ""}
          </p>
        </div>
      </div>
      <div className="_feed_inner_timeline_reaction">
        <button
          className={`_feed_inner_timeline_reaction_emoji _feed_reaction${liked ? " _feed_reaction_active" : ""}`}
          onClick={toggleLike}
        >
          <span className="_feed_inner_timeline_reaction_link">
            <span>
              {liked ? "❤️" : "🤍"} Like
            </span>
          </span>
        </button>
        <button
          className="_feed_inner_timeline_reaction_comment _feed_reaction"
          onClick={() => setShowComments((v) => !v)}
        >
          <span className="_feed_inner_timeline_reaction_link">
            <span>
              <svg className="_reaction_svg" xmlns="http://www.w3.org/2000/svg" width="21" height="21" fill="none" viewBox="0 0 21 21">
                <path stroke="#000" d="M1 10.5c0-.464 0-.696.009-.893A9 9 0 019.607 1.01C9.804 1 10.036 1 10.5 1v0c.464 0 .696 0 .893.009a9 9 0 018.598 8.598c.009.197.009.429.009.893v6.046c0 1.36 0 2.041-.317 2.535a2 2 0 01-.602.602c-.494.317-1.174.317-2.535.317H10.5c-.464 0-.696 0-.893-.009a9 9 0 01-8.598-8.598C1 11.196 1 10.964 1 10.5v0z" />
              </svg>
              Comment
            </span>
          </span>
        </button>
        <button className="_feed_inner_timeline_reaction_share _feed_reaction">
          <span className="_feed_inner_timeline_reaction_link">
            <span>Share</span>
          </span>
        </button>
      </div>
      {!showComments && latestComment && (
        <div className="_timline_comment_main _padd_r24 _padd_l24">
          {previousCount > 0 && (
            <div className="_previous_comment">
              <button
                type="button"
                className="_previous_comment_txt"
                onClick={() => setShowComments(true)}
              >
                View {previousCount} previous comment{previousCount !== 1 ? "s" : ""}
              </button>
            </div>
          )}
          <CommentItem comment={latestComment} />
        </div>
      )}
      {showComments && <CommentSection postId={post.id} />}
      {showLikedModal && (
        <WhoLikedModal targetType="post" targetId={post.id} onClose={() => setShowLikedModal(false)} />
      )}
    </div>
  );
}
