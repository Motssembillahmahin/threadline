export default function LeftSidebar() {
  return (
    <div className="_layout_left_sidebar_wrap">
      <div className="_layout_left_sidebar_inner">
        <div className="_left_inner_area_explore _padd_t24 _padd_b6 _padd_r24 _padd_l24 _b_radious6 _feed_inner_area">
          <h4 className="_left_inner_area_explore_title _title5 _mar_b24">Explore</h4>
          <ul className="_left_inner_area_explore_list">
            {[
              { label: "Learning", badge: "New" },
              { label: "Insights" },
              { label: "Find friends" },
              { label: "Bookmarks" },
              { label: "Group" },
              { label: "Gaming", badge: "New" },
              { label: "Settings" },
              { label: "Save post" },
            ].map((item) => (
              <li key={item.label} className="_left_inner_area_explore_item">
                <a href="#0" className="_left_inner_area_explore_link">
                  {item.label}
                </a>
                {item.badge && <span className="_left_inner_area_explore_link_txt">{item.badge}</span>}
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="_layout_left_sidebar_inner">
        <div className="_left_inner_area_suggest _padd_t24 _padd_b6 _padd_r24 _padd_l24 _b_radious6 _feed_inner_area">
          <div className="_left_inner_area_suggest_content _mar_b24">
            <h4 className="_left_inner_area_suggest_content_title _title5">Suggested People</h4>
            <span className="_left_inner_area_suggest_content_txt">
              <a className="_left_inner_area_suggest_content_txt_link" href="#0">See All</a>
            </span>
          </div>
          {[
            { name: "Steve Jobs", title: "CEO of Apple", img: "/assets/images/people1.png" },
            { name: "Ryan Roslansky", title: "CEO of Linkedin", img: "/assets/images/people2.png" },
            { name: "Dylan Field", title: "CEO of Figma", img: "/assets/images/people3.png" },
          ].map((person) => (
            <div key={person.name} className="_left_inner_area_suggest_info">
              <div className="_left_inner_area_suggest_info_box">
                <div className="_left_inner_area_suggest_info_image">
                  <img src={person.img} alt={person.name} className="_info_img" />
                </div>
                <div className="_left_inner_area_suggest_info_txt">
                  <h4 className="_left_inner_area_suggest_info_title">{person.name}</h4>
                  <p className="_left_inner_area_suggest_info_para">{person.title}</p>
                </div>
              </div>
              <div className="_left_inner_area_suggest_info_link">
                <a href="#0" className="_info_link">Connect</a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
