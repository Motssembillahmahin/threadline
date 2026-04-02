import { useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Post } from "@/types";

export function usePosts() {
  return useInfiniteQuery<Post[]>({
    queryKey: ["posts"],
    queryFn: async ({ pageParam }) => {
      const cursor = pageParam as string | undefined;
      const url = cursor ? `/api/posts?cursor=${encodeURIComponent(cursor)}&limit=10` : "/api/posts?limit=10";
      const res = await api.get<Post[]>(url);
      return res.data;
    },
    initialPageParam: undefined,
    getNextPageParam: (lastPage) => {
      if (!lastPage || lastPage.length < 10) return undefined;
      return lastPage[lastPage.length - 1].created_at;
    },
  });
}

export function useCreatePost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (formData: FormData) => {
      const res = await api.post<Post>("/api/posts", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    },
    onSuccess: (newPost) => {
      queryClient.setQueryData(["posts"], (old: { pages: Post[][] } | undefined) => {
        if (!old) return { pages: [[newPost]], pageParams: [undefined] };
        return {
          ...old,
          pages: [[newPost, ...old.pages[0]], ...old.pages.slice(1)],
        };
      });
    },
  });
}

export function useDeletePost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (postId: string) => {
      await api.delete(`/api/posts/${postId}`);
      return postId;
    },
    onSuccess: (postId) => {
      queryClient.setQueryData(["posts"], (old: { pages: Post[][] } | undefined) => {
        if (!old) return old;
        return {
          ...old,
          pages: old.pages.map((page) => page.filter((p) => p.id !== postId)),
        };
      });
    },
  });
}
