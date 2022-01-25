function closeForm() {
    document.getElementById("myForm").style.display = "none";
  }
  
  function myFunction() {
    var popup = document.getElementById("myPopup");
    popup.classList.toggle("show");
  }
  
  
  
  $(document).ready(function(){
  
    let btn = document.querySelector('.to-top-btn');
      let el = document.querySelector('.top-view');
      btn.addEventListener('click', function() {
          el.scrollIntoView(false);
      });
  
      // let btn2 = document.querySelector('.other-prod');
      // let el2 = document.querySelector('.from-ven');
      // btn2.addEventListener('click', function() {
      //     el2.scrollIntoView(false);
      // });
  
      $(".add").on('click', function(){
        var _pid=$(this).attr('data-product');
  
        $.ajax({
          url:"/add-to-wishlist",
          data:{
            product_id:_pid
          },
          dataType:'json',
          success:function(res){
            console.log(res)
            if (res.bool==true){ 
              $(".added2").css('visibility','hidden');
              show_fadeout = false;
              helper_text = $(".removed2").css('visibility','visible');
              show_fadeout = true;
  
            }else{
              if (res.bool==false){
                show_fadeout = true;
                helper_text = $(".added2").css('visibility','visible');
                show_fadeout = true;               
              }
            }
  
            if(show_fadeout) {
              helper_text.fadeIn();
                  helper_text.fadeOut(3000, function() {  });
              }
          }
        });      
      });
  
  
      
      $(".open-button").click(function(){
        $(".form-popup").toggle()
      });
  
      $(".cancel").click(function(){
        $(".form-popup").hide()
      });
  
  
  
      $(".compare").on('click', function(){
        var _cid=$(this).attr('data-compare');
  
        $.ajax({
          url:"/compare-items",
          data:{
            compare_id:_cid
          },
          dataType:'json',
          success:function(res){
  
            console.log(res)
            if (res){ 
              var product = sessionStorage.setItem('product',  JSON.stringify(res));
              var items = JSON.parse(sessionStorage.product);
              sessionStorage.setItem("lastname", JSON.stringify(items)); 
              console.log('items: ', items)              
  
            }
          }
        });      
      });
  
  
  
      
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  });