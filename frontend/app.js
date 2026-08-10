document
.getElementById("loginButton")
.addEventListener("click",function(){

    const username=document.getElementById("username").value;

    const password=document.getElementById("password").value;

    if(username==="" || password===""){

        alert("Lütfen kullanıcı adı ve şifre giriniz.");

        return;

    }

    alert("Giriş sistemi daha sonra eklenecek.");

});
