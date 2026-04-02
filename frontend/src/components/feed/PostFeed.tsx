"use client";

import { usePosts } from "@/hooks/usePosts";
import PostCard from "./PostCard";

export default function PostFeed() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading, isError } = usePosts();

  if (isLoading) return <div style={{ padding: 24 }}>Loading feed...</div>;
  if (isError) return <div style={{ padding: 24 }}>Failed to load posts.</div>;

  const posts = data?.pages.flat() ?? [];

  return (
    <div>
      {posts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
      {hasNextPage && (
        <div style={{ textAlign: "center", padding: "16px 0" }}>
          <button
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
            className="_feed_inner_text_area_btn_link"
          >
            {isFetchingNextPage ? "Loading..." : "Load more"}
          </button>
        </div>
      )}
      {!hasNextPage && posts.length > 0 && (
        <div style={{ textAlign: "center", padding: "16px 0", color: "#888", fontSize: 14 }}>
          You&apos;re all caught up!
        </div>
      )}
      {posts.length === 0 && (
        <div style={{ textAlign: "center", padding: 32, color: "#888" }}>
          No posts yet. Be the first to post!
        </div>
      )}
    </div>
  );
}
