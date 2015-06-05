<?php 
if (!$USER_IDENTIFIED) 
{
?>
	<h3 align=center>Please enter your information below.</h3>
<?php 
} else {
?>
	<h3 align=center>Please enter a person's information below.</h3>
<?php 
}
?>
<form method="post" id="registrationform" name="registrationform" action="/cgi-bin/catan_script.cgi">
<!-- Hidden inputs -->
<input id="geo_location" type="hidden" name="submitter_gps" value="" />

<div class="field">
	<span class="label">Family Name:</span>
	<span class="value"><input type="text" name="name_family" id="name_family" <?php 
	if (isset($_GET) && isset($_GET['name_family'])) {
		echo 'value="'.$_GET['name_family'].'"';
	}
	?>/></span>
</div>

<div class="field">
	<span class="label">Given Name:</span>
	<span class="value"><input type="text" name="name_given" id="name_given"/ <?php 
	if (isset($_GET) && isset($_GET['name_given'])) {
		echo 'value="'.$_GET['name_given'].'"';
	}
	?>></span>
</div>

<div class="field">
	<span class="label">Sex:</span>
	<span class="value"><select name="sex" id="sex">
		<option value="" selected></option>
		<option value="female">female</option>
		<option value="male">male</option>
		<option value="other">other</option>
		</select></span>
		
</div>	
<div class="field">
	<span class="label">Age:</span>
	<span class="value"><input type="text" name="age" id="age"></span>
</div>
<div class="field">
	<span class="label">I am this person:</span>
	<span class="value"><input type="checkbox" name="user_is_submitter" id="user_is_submitter" <?php 
	if (!$USER_IDENTIFIED)
		echo "checked disabled";
	?>></span>
</div>
<div class="field" style="text-align:center;">
	<input type="submit">
</div>
</form>
