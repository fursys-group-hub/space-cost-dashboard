(function(){var DATA={spaces:window.__SPACES,details:window.__DETAILS};var draws={};
function run(name){var fn=draws[name];if(!fn)return;document.querySelectorAll('[data-draw="'+name+'"]').forEach(function(el){try{fn(el);}catch(e){console.error(e);}});}
window.dash={colors:['#C6AEE0','#838806','#0075EA','#F47018','#37847D'],
data:function(id){var d=DATA[id];return d?{status:'ok',data:d,message:null,refreshing:false}:{status:'missing',data:[]};},
draw:function(name,fn){if(fn){draws[name]=fn;}run(name);},onData:function(fn){fn();},setLink:function(){},params:function(){return {};},setParams:function(){},refresh:function(){}};
var w=window.innerWidth,t;window.addEventListener('resize',function(){if(window.innerWidth===w)return;w=window.innerWidth;clearTimeout(t);t=setTimeout(function(){['brand-chart','year-chart'].forEach(function(n){run(n);});},150);});})();