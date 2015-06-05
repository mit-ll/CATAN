<?php
require 'simple_html_dom.php';

// Get our signal quality
$content_signal = file_get_contents("http://localnode:8080/cgi-bin/signal");

// Extract relevant data
$oHTML = str_get_html($content_signal);

// Get all of our rows
$oTRs = $oHTML->find('table tr');
// Extract the first row with our signal/noise data
$oTDs = $oTRs[1]->find('td');
$aRow = array();
foreach($oTDs as $oTD) {
	$aRow[] = trim($oTD->plaintext);
}

// Store the important data to be displayed later
$SIGNAL = $aRow[1];
$NOISE = $aRow[3];
$RATIO = $aRow[5];



// Get our mesh status
$content_signal = file_get_contents("http://localnode:8080/cgi-bin/mesh");

// Extract relevant data
$oHTML = str_get_html($content_signal);

// Get all of our rows
$mesh_table = $oHTML->find('table')[0];

?>

<h1 align="center">Current Router Status</h1>
<div id="signal_noise" style="text-align:center; font-size: 150%;margin-bottom:2%;">
<span>Signal: <b><?php echo $SIGNAL; ?></b>  </span>
<span>Noise: <b><?php echo $NOISE; ?></b>  </span>
<span>Ratio: <b><?php echo $RATIO; ?></b>  </span>
</div>
<div id="mesh_table" style="text-align:center; margin-bottom:2%;">
<?php echo $mesh_table; ?>
</div>