window.addEventListener('DOMContentLoaded', runFunction);

// * == Run!!!! ======== * //
function runFunction() {
  mainHeight();
  menu();
  resizingTimeoutFunction();
  readDeviceOrientation();
}

// * == (Read device orientation) ======== * //
function readDeviceOrientation() {
  window.addEventListener(
    'orientationchange',
    function () {
      setTimeOutF(mainHeight);
    },
    false
  );
}

// * == (Resizing) ======== * //
function resizingTimeoutFunction() {
  setTimeOutF(resizing);

  function resizing() {
    // window.onresize = mainHeight, removeActive;
    window.onresize = resizeAll;
  }
}

function resizeAll() {
  mainHeight();
  removeActive();
}

// * == (SetTimeOut) ======== * //
function setTimeOutF(rsto) {
  var resizingTimeout;

  clearTimeout(resizingTimeout);
  resizingTimeout = setTimeout(rsto, 300);
}

// * == (Detect main height) ======== * //
function mainHeight() {
  var header = document.getElementById('header');
  var main = document.getElementById('content');
  var footer = document.getElementById('footer');

  var headerH = header.getBoundingClientRect().height || 0;
  var mainH = main.getBoundingClientRect().height || 0;
  var footerH = footer.getBoundingClientRect().height || 0;
  var windowH =
    window.innerHeight ||
    document.documentElement.clientHeight ||
    document.body.clientHeight;

  var mainMinH = windowH - headerH - footerH;

  main.style.minHeight = mainMinH + 'px';

  // console.log('windowH :' + windowH + 'px','headerH :' + headerH + 'px', 'mainMinH :' + mainMinH + 'px', 'footerH :' + footerH + 'px');

  if (mainH < mainMinH) {
    main.style.minHeight = mainMinH + 'px';
    // console.log('mainH < mainMinH, mainMinH :' + mainMinH + 'px', 'mainH :' + mainH + 'px');
  }
  // alert('메인');
}

// * == (Menu check) ======== * //
function menu() {
  var mainmenu = document.getElementById('mainMenu');
  var menuchildren = mainmenu.children;
  var menuGrandChildren = mainmenu.getElementsByTagName('ul');

  for (var i = 0; i < menuGrandChildren.length; i++) {
    var div = menuGrandChildren.item(i);
    var divp = div.parentElement.parentElement;
    addClass(divp, 'has-child');

    divp.onclick = toggleCollapse;
  }
}

function toggleCollapse() {
  var element = this;

  if (element.classList) {
    element.classList.toggle('is-visible');
  } else {
    var classes = element.className.split('');
    var i = classes.indexOf('is-visible');

    if (i >= 0) classes.splice(i, 1);
    else classes.push('is-visible');
    element.className = classes.join('');
  }
}

// * == (Mobile sidebar) ======== * //
function removeActive() {
  var wrap = document.getElementById('wrap');
  var mainmenu = document.getElementById('mainMenu');
  var menuchildren = mainmenu.children;
  var menuGrandChildren = mainmenu.getElementsByTagName('ul');

  if (window.innerWidth >= 1200) {
    removeClass(wrap, 'is-active');
  }
}

// * == (AddClass) ======== * //
function addClass(element, className) {
  element.className += ' ' + className;
}

// * == (RemoveClass) ======== * //
function removeClass(element, className) {
  var check = new RegExp('(\\s|^)' + className + '(\\s|$)');
  element.className = element.className.replace(check, ' ').trim();
}
