import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Reply } from "@/types";

export function useReplies(commentId: string, enabled: boolean) {
  return useQuery<Reply[]>({
    queryKey: ["replies", commentId],
    queryFn: async () => {
      const res = await api.get<Reply[]>(`/api/replies/comment/${commentId}`);
      return res.data;
    },
    enabled,
  });
}

export function useCreateReply(commentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (content: string) => {
      const res = await api.post<Reply>(`/api/replies/comment/${commentId}`, { content });
      return res.data;
    },
    onSuccess: (newReply) => {
      queryClient.setQueryData(["replies", commentId], (old: Reply[] | undefined) => {
        return [...(old || []), newReply];
      });
    },
  });
}
