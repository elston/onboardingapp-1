

function gradient(id, level)
{
	var box = document.getElementById(id);
	box.style.opacity = level;
	box.style.MozOpacity = level;
	box.style.KhtmlOpacity = level;
	box.style.filter = "alpha(opacity=" + level * 100 + ")";
	box.style.display="block";
	return;
}


function fadein(id) 
{
	var level = 0;
	while(level <= 1)
	{
		setTimeout( "gradient('" + id + "'," + level + ")", (level* 1000) + 10);
		level += 0.01;
	}
}


// Open the lightbox 

function open_changeteamowner_box(formtitle, fadin) {
  var box = document.getElementById('changeteamowner_box'); 
  document.getElementById('shadowing').style.display='block';

  var btitle = document.getElementById('lightbox_content_heading');
  btitle.innerHTML = formtitle;
  
  if(fadin){
    gradient("box", 0);
    fadein("box");
  }else{   
    box.style.display='block';
  }   
};

function open_team_editbox(formtitle, fadin) {
  var box = document.getElementById('team_editbox'); 
  document.getElementById('shadowing').style.display='block';

  var btitle = document.getElementById('lightbox_content_heading');
  btitle.innerHTML = formtitle;
  
  if(fadin){
    gradient("box", 0);
    fadein("box");
  }else{   
    box.style.display='block';
  }   
};

function openbox(formtitle, fadin)
{
  var box = document.getElementById('box'); 
  document.getElementById('shadowing').style.display='block';

  var btitle = document.getElementById('lightbox_content_heading');
  btitle.innerHTML = formtitle;
  
  if(fadin)
  {
	 gradient("box", 0);
	 fadein("box");
  }
  else
  { 	
    box.style.display='block';
  }  	
}
function openbox2(formtitle, fadin)
{
  var box = document.getElementById('box2'); 
  document.getElementById('shadowing').style.display='block';

  var btitle = document.getElementById('lightbox_content_heading');
  btitle.innerHTML = formtitle;
  
  if(fadin)
  {
	 gradient("box2", 0);
	 fadein("box2");
  }
  else
  { 	
    box.style.display='block';
  }  	
}
function openbox22(formtitle, fadin)
{
  var box = document.getElementById('box22'); 
  document.getElementById('shadowing22').style.display='block';

  var btitle = document.getElementById('lightbox_content_heading22');
  btitle.innerHTML = formtitle;
  
  if(fadin)
  {
	 gradient("box22", 0);
	 fadein("box22");
  }
  else
  { 	
    box.style.display='block';
  }  	
}

function clear_inputs()
{
	document.getElementById("btn_change_name").setAttribute("name","submit");
	var fields = document.getElementsByTagName('input');
    for(var i=0, len=fields.length; i < len; i++) 
	{
        var field = fields[i];
        switch(field.type)
        {
            case 'radio':
            case 'checkbox':
                field.checked = false;
                break;

            case 'text':
            case 'password':
            case 'hidden':
                field.value = ''
        }
	}
}


// Close the lightbox

function closebox()
{
   document.getElementById('box').style.display='none';
   document.getElementById('shadowing').style.display='none';
}
function closebox2()
{
   document.getElementById('box2').style.display='none';
   document.getElementById('shadowing').style.display='none';
}
function closebox22()
{
   document.getElementById('box22').style.display='none';
   document.getElementById('shadowing22').style.display='none';
}

function close_team_edtbox(){
   document.getElementById('team_editbox').style.display='none';
   document.getElementById('shadowing').style.display='none';
}

function close_changeteamowner_box(){
   document.getElementById('changeteamowner_box').style.display='none';
   document.getElementById('shadowing').style.display='none';
}

