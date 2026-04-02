export interface User {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  avatar_url: string | null;
  created_at: string;
}

export interface Author {
  id: string;
  first_name: string;
  last_name: string;
  avatar_url: string | null;
}

export interface Post {
  id: string;
  content: string | null;
  image_url: string | null;
  visibility: "public" | "private";
  like_count: number;
  comment_count: number;
  created_at: string;
  author: Author;
  liked_by_me: boolean;
}

export interface Comment {
  id: string;
  content: string;
  like_count: number;
  reply_count: number;
  created_at: string;
  author: Author;
  liked_by_me: boolean;
}

export interface Reply {
  id: string;
  content: string;
  like_count: number;
  created_at: string;
  author: Author;
  liked_by_me: boolean;
}

export interface LikedUser {
  id: string;
  first_name: string;
  last_name: string;
  avatar_url: string | null;
}
