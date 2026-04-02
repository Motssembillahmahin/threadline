export default function RightSidebar() {
  return (
    <div className="_layout_right_sidebar_wrap">
      <div className="_layout_right_sidebar_inner">
        <div className="_right_inner_area_info _padd_t24 _padd_b24 _padd_r24 _padd_l24 _b_radious6 _feed_inner_area">
          <div className="_right_inner_area_info_content _mar_b24">
            <h4 className="_right_inner_area_info_content_title _title5">You Might Like</h4>
            <span className="_right_inner_area_info_content_txt">
              <a className="_right_inner_area_info_content_txt_link" href="#0">See All</a>
            </span>
          </div>
          <hr className="_underline" />
          {[
            { name: "Radovan SkillArena", title: "Founder & CEO at Trophy", img: "/assets/images/Avatar.png" },
            { name: "Steve Jobs", title: "CEO of Apple", img: "/assets/images/people1.png" },
          ].map((person) => (
            <div key={person.name} className="_right_inner_area_info_ppl">
              <div className="_right_inner_area_info_box">
                <div className="_right_inner_area_info_box_image">
                  <img src={person.img} alt={person.name} className="_ppl_img" />
                </div>
                <div className="_right_inner_area_info_box_txt">
                  <h4 className="_right_inner_area_info_box_title">{person.name}</h4>
                  <p className="_right_inner_area_info_box_para">{person.title}</p>
                </div>
              </div>
              <div className="_right_info_btn_grp">
                <button type="button" className="_right_info_btn_link">Ignore</button>
                <button type="button" className="_right_info_btn_link _right_info_btn_link_active">Follow</button>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="_layout_right_sidebar_inner">
        <div className="_feed_right_inner_area_card _padd_t24 _padd_b6 _padd_r24 _padd_l24 _b_radious6 _feed_inner_area">
          <div className="_feed_top_fixed">
            <div className="_feed_right_inner_area_card_content _mar_b24">
              <h4 className="_feed_right_inner_area_card_content_title _title5">Your Friends</h4>
              <span className="_feed_right_inner_area_card_content_txt">
                <a className="_feed_right_inner_area_card_content_txt_link" href="#0">See All</a>
              </span>
            </div>
          </div>
          <div className="_feed_bottom_fixed">
            {[
              { name: "Steve Jobs", title: "CEO of Apple", img: "/assets/images/people1.png", online: false },
              { name: "Ryan Roslansky", title: "CEO of Linkedin", img: "/assets/images/people2.png", online: true },
              { name: "Dylan Field", title: "CEO of Figma", img: "/assets/images/people3.png", online: true },
            ].map((person) => (
              <div key={person.name} className={`_feed_right_inner_area_card_ppl${!person.online ? " _feed_right_inner_area_card_ppl_inactive" : ""}`}>
                <div className="_feed_right_inner_area_card_ppl_box">
                  <div className="_feed_right_inner_area_card_ppl_image">
                    <img src={person.img} alt={person.name} className="_box_ppl_img" />
                  </div>
                  <div className="_feed_right_inner_area_card_ppl_txt">
                    <h4 className="_feed_right_inner_area_card_ppl_title">{person.name}</h4>
                    <p className="_feed_right_inner_area_card_ppl_para">{person.title}</p>
                  </div>
                </div>
                <div className="_feed_right_inner_area_card_ppl_side">
                  {person.online ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 14 14">
                      <rect width="12" height="12" x="1" y="1" fill="#0ACF83" stroke="#fff" strokeWidth="2" rx="6" />
                    </svg>
                  ) : (
                    <span>offline</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
