$(document).ready(function () {
    listing();
});

// 좋아요 post
function toggle_like(post_id, type) {
    console.log(post_id, type)
    let $a_like = $(`#${post_id} a[aria-label='heart']`)
    let $i_like = $a_like.find("i")
    if ($i_like.hasClass("fa-heart-o")) {
        $.ajax({
            type: 'POST',
            url: '/update-like',
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "like"
            },
            success: function (response) {
                console.log("like")
                $i_like.addClass("fa-heart").removeClass("fa-heart-o")
                $a_like.find("span.like-num").text(num2str(response["count"]))
            }
        })
    } else {
        $.ajax({
            type: "POST",
            url: "/update-like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "unlike"
            },
            success: function (response) {
                console.log("unlike")
                $i_like.addClass("fa-heart-o").removeClass("fa-heart")
                $a_like.find("span.like-num").text(response["count"])
            }
        })

    }
}

// 글, 좋아요 get
function listing() {
    $("#post-wrap").empty()
    $.ajax({
        type: "GET",
        url: "/get-posts",
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let rows = response["posts"]
                for (let i = 0; i < rows.length; i++) {
                    let post = rows[i]
                    let profile_name = rows[i]["profile_name"]
                    let ytburl = rows[i]["ytburl"]
                    let ytbcode = rows[i]["ytbcode"]
                    let comment = rows[i]["comment"]
                    let feel = rows[i]["feel"]
                    let file = rows[i]["file"]
                    let time_post = new Date(post["date"])
                    let time_before = time2str(time_post)
                    let class_heart = post['heart_by_me'] ? "fa-heart" : "fa-heart-o"
                    let count_heart = post['count_heart']
                    let temp_html = `<div class="post-box" id="${post["_id"]}">
                                                <div class="post-header">
                                                    <p class="post-profile">@${profile_name}</p>
                                                    <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                                        <span class="icon is-small"><i class="fa ${class_heart}" aria-hidden="true"></i></span>
                                                        <span class="like-num">${num2str(count_heart)}</span>
                                                    </a>
                                                    <p class="post-feel">${feel}</p>
                                                </div>
                                                <div class="post-body">
                                                    <img class="post-image" src="static/img/${file}" alt="">
                                                </div>
                                                <div class="post-footer">
                                                    <iframe class="ytb-player" width="100" height="100"
                                                            src="https://www.youtube.com/embed/${ytbcode}?controls=0&disablekb=1&rel=0&modestbranding=1&enablejsapi=1&version=3&playerapiid=ytplayer"
                                                            title="YouTube video player"
                                                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                                            allowfullscreen>
                                                    </iframe>
                                                    <p class="post-content">${comment}</p>
                                                </div>
                                            </div>`
                    $(".post-wrap").append(temp_html)
                }
            }
        }
    })
}

// 포스팅.파일 업로드
function posting() {
    let ytbrul = $('#ytburl').val()
    let comment = $('#comment').val()
    let file = $('#upload_file')[0].files[0]
    let feel = $('[name=feelbtn1]:checked').val();
    let form_data = new FormData()
    form_data.append("file_give", file)
    form_data.append("ytburl_give", ytbrul)
    form_data.append("comment_give", comment)
    form_data.append("feel_give", feel)
    $.ajax({
        type: "POST",
        url: "/upload",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            if (response['result'] == 'success') {
                window.location.reload()
            } else {
                alert(response['msg'])
            }
        }
    });
}

// 로그아웃
function logout() {
    $.removeCookie('mytoken', {path: '/'});
    window.location.href = '/';
}

// 좋아요 숫자 표시 변환
function num2str(count) {
    if (count > 10000) {
        return parseInt(count / 1000) + "k"
    }
    if (count > 500) {
        return parseInt(count / 100) / 10 + "k"
    }
    if (count == 0) {
        return ""
    }
    return count
}

// 시간 표시 변환
function time2str(date) {
    let today = new Date()
    let time = (today - date) / 1000 / 60  // 분

    if (time < 60) {
        return parseInt(time) + "분 전"
    }
    time = time / 60  // 시간
    if (time < 24) {
        return parseInt(time) + "시간 전"
    }
    time = time / 24
    if (time < 7) {
        return parseInt(time) + "일 전"
    }
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

