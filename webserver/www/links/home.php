<?php
if ($USER_IDENTIFIED) { 
	echo "<h3 align=center>Search for a person.</h3>";
} else {
	echo "<h3 align=center>Please enter your name below.</h3>";
	
}
?>
<form method="get" id="searchform" name="searchform">
<!-- Hidden inputs -->
<input id="geo_location" type="hidden" name="submitter_gps" value="NA" />
<input type="hidden" name="l" value="search"/>

<div class="field">
	<span class="label">Family Name:</span>
	<span class="value"><input type="text" name="name_family" id="name_family"/></span>
</div>

<div class="field">
	<span class="label">Given Name:</span>
	<span class="value"><input type="text" name="name_given" id="name_given"/></span>
</div>

<div class="field" style="text-align:center;margin:1%;">
	<input type="submit">
</div>
</form>