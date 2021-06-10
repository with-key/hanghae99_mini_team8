$(document).ready(function () {
  post_before();
});

const currentId = '{{user_id}}'; // 접속자 아이디

console.log(currentId);

function post_before() {
  $.ajax({
    type: 'GET',
    url: '/post',
    data: {},
    success: function (response) {
      let userID = response['userid'];
      // console.log(userID)
    },
  });
}

function clickFunct() {
  registerValdation();
  post();
}

// 폼 벨리데이션
function registerValdation() {
  let postnameSelct = $('#input-postname');
  let useridSelct = $('#input-userid');
  let categoriesSelct = $("input[name='radio-category']:checked");
  let mdurlSelct = $('#input-url');
  let gradeSelct = $("input[name='radio-score']:checked");
  let recommendationSelct = $('#input-recommendation');
  let honeytipSelct = $('#input-honeytip');

  let postname_val = postnameSelct.val(); // 글제목
  let userid_val = useridSelct.val(); // 작성자
  let categories_val = categoriesSelct.val(); // 카테고리
  let mdurl_val = mdurlSelct.val(); // URL
  let grade_val = gradeSelct.val(); // 평점
  let recommendation_val = recommendationSelct.val(); // 좋았던 점
  let honeytip_val = honeytipSelct.val(); // 꿀팁

  // == 1. postname
  if (postname_val == '') {
    postnameSelct.siblings('.validation-message').text('제목을 입력해주세요.');
    postnameSelct.focus();
    return;
  } else {
    postnameSelct.text('');
  }

  // == 2. categories
  if (categories_val == undefined) {
    $("input[name='radio-category']")
      .parent()
      .siblings('.validation-message')
      .text('카테고리를 선택해주세요.');
    return;
  } else {
    categoriesSelct.text('');
  }

  // == 3. mdurl
  if (mdurl_val == '') {
    mdurlSelct
      .siblings('.validation-message')
      .text('공유하고 싶은 상품링크를 입력해주세요.');
    mdurlSelct.focus();
    return;
  } else {
    mdurlSelct.text('');
  }

  // == 4. grade
  if (grade_val == undefined) {
    $("input[name='radio-score']")
      .parent()
      .siblings('.validation-message')
      .text('평점을 선택해주세요.');
    return;
  } else {
    gradeSelct.text('');
  }

  // == 5. postname
  if (recommendation_val == '') {
    recommendationSelct
      .siblings('.validation-message')
      .text('좋았던 점을 입력해주세요.');
    recommendationSelct.focus();
    return;
  } else {
    recommendationSelct.text('');
  }

  // == 6. honeytip
  if (honeytip_val == '') {
    honeytipSelct.siblings('.validation-message').text('꿀팁을 입력해주세요.');
    honeytipSelct.focus();
    return;
  } else {
    honeytipSelct.text('');
  }
}

// 포스트
function post() {
  let postname_val = $('#input-postname').val(); // 글제목
  let userid_val = $('#input-userid').val(); // 작성자
  let categories_val = $("input[name='radio-category']:checked").val(); // 카테고리
  let mdurl_val = $('#input-url').val(); // URL
  let grade_val = $("input[name='radio-score']:checked").val(); // 평점
  let recommendation_val = $('#input-recommendation').val(); // 좋았던 점
  let honeytip_val = $('#input-honeytip').val(); // 꿀팁
  let today = new Date();

  $.ajax({
    type: 'POST',
    url: '/post',
    data: {
      postname: postname_val,
      userid: userid_val,
      categories: categories_val,
      mdurl: mdurl_val,
      grade: grade_val,
      recommendation: recommendation_val,
      honeytip: honeytip_val,
      date: Date.now(),
    },
    success: function (response) {
      let msg = response['msg'];

      if (msg == 'success') {
        window.location.href = '/main';
        alert('꿀템이 등록되었습니다!');
      } else if (msg == 'fail') {
        alert('url을 확인해주세요!');
      }
    },
  });
}
