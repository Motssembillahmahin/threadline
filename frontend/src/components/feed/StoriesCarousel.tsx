export default function StoriesCarousel() {
  const stories = [
    { name: "Ryan Roslansky", img: "/assets/images/public_story.png" },
    { name: "Steve Jobs", img: "/assets/images/public_story.png" },
    { name: "Dylan Field", img: "/assets/images/public_story.png" },
  ];

  return (
    <div className="_feed_inner_ppl_card _mar_b16">
      <div className="_feed_inner_story_arrow">
        <button type="button" className="_feed_inner_story_arrow_btn">
          <svg xmlns="http://www.w3.org/2000/svg" width="9" height="8" fill="none" viewBox="0 0 9 8">
            <path fill="#fff" d="M8 4l.366-.341.318.341-.318.341L8 4zm-7 .5a.5.5 0 010-1v1zM5.566.659l2.8 3-.732.682-2.8-3L5.566.66zm2.8 3.682l-2.8 3-.732-.682 2.8-3 .732.682zM8 4.5H1v-1h7v1z" />
          </svg>
        </button>
      </div>
      <div className="row">
        <div className="col-xl-3 col-lg-3 col-md-4 col-sm-4 col">
          <div className="_feed_inner_profile_story _b_radious6">
            <div className="_feed_inner_profile_story_image">
              <div className="_feed_inner_story_txt">
                <div className="_feed_inner_story_btn">
                  <button className="_feed_inner_story_btn_link">+</button>
                </div>
              </div>
            </div>
            <p className="_feed_inner_story_para">Your Story</p>
          </div>
        </div>
        {stories.map((s) => (
          <div key={s.name} className="col-xl-3 col-lg-3 col-md-4 col-sm-4 col">
            <div className="_feed_inner_public_story _b_radious6">
              <div className="_feed_inner_public_story_image">
                <img src={s.img} alt={s.name} style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: 8 }} />
              </div>
              <div className="_feed_inner_pulic_story_txt">
                <p className="_feed_inner_pulic_story_para">{s.name}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
