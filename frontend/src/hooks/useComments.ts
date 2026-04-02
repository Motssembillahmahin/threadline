import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Comment } from "@/types";

export function useComments(postId: string, enabled: boolean) {
  return useQuery<Comment[]>({
    queryKey: ["comments", postId],
    queryFn: async () => {
      const res = await api.get<Comment[]>(`/api/comments/post/${postId}`);
      return res.data;
    },
    enabled,
  });
}

export function useCreateComment(postId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (content: string) => {
      const res = await api.post<Comment>(`/api/comments/post/${postId}`, { content });
      return res.data;
    },
    onSuccess: (newComment) => {
      queryClient.setQueryData(["comments", postId], (old: Comment[] | undefined) => {
        return [...(old || []), newComment];
      });
      // Update comment_count in posts cache
      queryClient.setQueryData(["posts"], (old: { pages: { id: string; comment_count: number }[][] } | undefined) => {
        if (!old) return old;
        return {
          ...old,
          pages: old.pages.map((page) =>
            page.map((p) => (p.id === postId ? { ...p, comment_count: p.comment_count + 1 } : p))
          ),
        };
      });
    },
  });
}
