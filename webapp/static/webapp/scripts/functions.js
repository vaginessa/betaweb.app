String.prototype.trim=function(){return this.replace(/^\s+|\s+$/g, '');};
String.prototype.isJson=function(){var r=true; try{JSON.parse(this);}catch(e){r=false;}return r;};
String.prototype.isValidInstaUsername=function(){if(/^[a-zA-Z0-9_.@]+$/.test(this)){return true;}else{return false;}};
String.prototype.isValidInstaReel=function(){if(/^[a-zA-Z0-9_-]+$/.test(this)){return true;}else{return false;}};
String.prototype.isValidInstaPost=function(){if(/^[a-zA-Z0-9_-]+$/.test(this)){return true;}else{return false;}};
String.prototype.isValidTikVideo=function(){if(/^[a-zA-Z0-9]+$/.test(this)){return true;}else{return false;}};
String.prototype.commas=function(){return this.replace(/\B(?=(\d{3})+(?!\d))/g, ",");};