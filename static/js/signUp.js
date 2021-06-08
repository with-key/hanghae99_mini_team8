// 아이디 중복체크
const id = document.getElementById('sign_id');
const validBtn = document.getElementById('valid_btn');

console.log(id);
console.log(validBtn);

const vaildOverlapId = (e) => {
  console.log(e);
};
const onChangeHandler = (e) => {
  console.log(e);
};

validBtn.onclick = vaildOverlapId;
id.onkeydown = onChangeHandler;
// 회원가입 완료
