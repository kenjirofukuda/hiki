#
#
#
def mytube(vcode)
<<-EOF
<object width="425" height="344">
<param name="movie" 
  value="http://www.youtube.com/v/#{vcode}">
</param>
<param name="allowFullScreen" value="true"></param>
<param name="allowscriptaccess" value="always"></param>
<embed src="http://www.youtube.com/v/#{vcode}" 
  type="application/x-shockwave-flash" 
  allowscriptaccess="always" 
  allowfullscreen="true" width="425" height="344">
</embed>
</object>
EOF
end
