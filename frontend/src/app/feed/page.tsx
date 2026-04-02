import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import Navbar from "@/components/layout/Navbar";
import LeftSidebar from "@/components/layout/LeftSidebar";
import RightSidebar from "@/components/layout/RightSidebar";
import CreatePostBox from "@/components/feed/CreatePostBox";
import PostFeed from "@/components/feed/PostFeed";
import StoriesCarousel from "@/components/feed/StoriesCarousel";
import DarkModeToggle from "@/components/ui/DarkModeToggle";

export default async function FeedPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token");
  if (!token) {
    redirect("/login");
  }

  return (
    <div className="_layout _layout_main_wrapper">
      <DarkModeToggle />
      <div className="_main_layout">
        <Navbar />
        <div className="container _custom_container">
          <div className="row">
            <div className="col-xl-3 col-lg-3 col-md-12 col-sm-12">
              <LeftSidebar />
            </div>
            <div className="col-xl-6 col-lg-6 col-md-12 col-sm-12">
              <div className="_layout_middle_wrap">
                <div className="_layout_middle_inner">
                  <StoriesCarousel />
                  <CreatePostBox />
                  <PostFeed />
                </div>
              </div>
            </div>
            <div className="col-xl-3 col-lg-3 col-md-12 col-sm-12">
              <RightSidebar />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
