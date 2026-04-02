"use client";

import { useRef, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useCreatePost } from "@/hooks/usePosts";

export default function CreatePostBox() {
  const { user } = useAuth();
  const [content, setContent] = useState("");
  const [visibility, setVisibility] = useState<"public" | "private">("public");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const createPost = useCreatePost();

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim() && !imageFile) return;
    const formData = new FormData();
    if (content.trim()) formData.append("content", content);
    formData.append("visibility", visibility);
    if (imageFile) formData.append("image", imageFile);
    await createPost.mutateAsync(formData);
    setContent("");
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  return (
    <div className="_feed_inner_text_area _b_radious6 _padd_b24 _padd_t24 _padd_r24 _padd_l24 _mar_b16">
      <form onSubmit={handleSubmit}>
        <div className="_feed_inner_text_area_box">
          <div className="_feed_inner_text_area_box_image">
            <img
              src={user?.avatar_url || "/assets/images/profile.png"}
              alt=""
              className="_post_author_img"
              style={{ width: 40, height: 40, borderRadius: "50%", objectFit: "cover" }}
            />
          </div>
          <div className="form-floating _feed_inner_text_area_box_form">
            <textarea
              className="form-control"
              placeholder="What's on your mind?"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              style={{ height: 80 }}
            />
          </div>
        </div>
        {imagePreview && (
          <div style={{ marginTop: 8 }}>
            <img src={imagePreview} alt="preview" style={{ maxWidth: "100%", borderRadius: 8, maxHeight: 200, objectFit: "cover" }} />
            <button type="button" onClick={() => { setImageFile(null); setImagePreview(null); }} style={{ marginLeft: 8 }}>
              Remove
            </button>
          </div>
        )}
        <div className="_feed_inner_text_area_bottom">
          <div className="_feed_inner_text_area_item">
            <div className="_feed_inner_text_area_bottom_photo _feed_common">
              <button type="button" className="_feed_inner_text_area_bottom_photo_link" onClick={() => fileInputRef.current?.click()}>
                <span className="_feed_inner_text_area_bottom_photo_iamge _mar_img">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 20 20">
                    <path fill="#666" fillRule="evenodd" d="M14.243 2C16.874 2 18 3.252 18 6.054v7.892C18 16.748 16.874 18 14.243 18H5.757C3.126 18 2 16.748 2 13.946V6.054C2 3.252 3.126 2 5.757 2h8.486zm0 1.5H5.757C4.012 3.5 3.5 4.148 3.5 6.054v7.892c0 1.906.512 2.554 2.257 2.554h.901l4.63-5.283a1 1 0 011.444-.072l.084.086L14.6 13.32l.058-.072a1.75 1.75 0 012.342.072V6.054c0-1.906-.512-2.554-2.757-2.554zM7.25 5.5a1.75 1.75 0 110 3.5 1.75 1.75 0 010-3.5z" clipRule="evenodd" />
                  </svg>
                  Photo
                </span>
              </button>
              <input ref={fileInputRef} type="file" accept="image/*" style={{ display: "none" }} onChange={handleFileChange} />
            </div>
            <div className="_feed_inner_text_area_bottom_video _feed_common">
              <select
                value={visibility}
                onChange={(e) => setVisibility(e.target.value as "public" | "private")}
                className="form-control"
                style={{ width: "auto", display: "inline-block" }}
              >
                <option value="public">Public</option>
                <option value="private">Private</option>
              </select>
            </div>
          </div>
          <div className="_feed_inner_text_area_btn">
            <button type="submit" className="_feed_inner_text_area_btn_link" disabled={createPost.isPending}>
              {createPost.isPending ? "Posting..." : "Post"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
