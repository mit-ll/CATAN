<?php 
// Report all errors for debugging
ini_set('error_reporting', E_ALL);
ini_set('display_errors', 'on');
ini_set('display_errors', 1);
error_reporting(E_ALL);
require('catan.include.php');
?>

<!DOCTYPE html>
<html>
<head>
	<link rel="stylesheet" type="text/css" href="catan.css">
	<script src="jquery-1.11.1.min.js"></script>
</head>
<body onload="getLocation()">



<div id="content">
	<div id="header">
		LL Emergency Network

	</div>
	
	<?php
		$include_link = $LINK_DIR.$DEFAULT_LINK;

		if ($_SESSION['USER_INFO']) {
			$person_id = $_SESSION['USER_INFO']['person_id'];
			$name_family = $_SESSION['USER_INFO']['name_family'];
			$name_given = $_SESSION['USER_INFO']['name_given'];
			
			echo '<div id="user_info">Device associated with ';
			echo '<a href="?l=profile&pid='.$person_id.'"><b><i>';
			echo $name_given.' '.$name_family;
			echo '</i></b></a> ';
			//echo '<span><a href="?logout=1">(Logout)</a>.</span>';
			echo'</div>';
			
			$USER_IDENTIFIED = true;
		} else {
			$USER_IDENTIFIED = false;
		}
		
 		if (isset($_GET) && isset($_GET['l'])) {
 			$link_name = $LINK_DIR.$_GET['l'].".php";
 			if (file_exists($link_name)) {
 				$include_link = $link_name;
 			}
 		}
 	?>
 	
 	<?php
		include($include_link);
	?>

</div>

<div id="footer">
	<img src="images/LL Logo blue 72 dpi jpg.jpg"><BR/>
	<div>Powered by CATAN (<?php echo $conf_file['node_id']; ?>)
</div>

<script src="catan.js"></script>
</body>
</html>