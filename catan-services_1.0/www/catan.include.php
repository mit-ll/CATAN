<?php
// Report all errors for debugging
ini_set('error_reporting', E_ALL);
ini_set('display_errors', 'on');
ini_set('display_errors', 1);
error_reporting(E_ALL);

session_start();

// Set our redirect address
$addr = $_SERVER['SERVER_ADDR'];

// If DNS redirect is on, let's use a fancy name
exec("pgrep catan_dns", $output, $return);
if ($return == 0 && $addr == "192.168.2.1") {
    $addr = "CATAN";
}
// Ensure that we always point to the same address (important for cookies and sanity)
if (strcasecmp($addr,$_SERVER['HTTP_HOST']) != 0)
{
    echo '<META HTTP-EQUIV=REFRESH CONTENT="0; URL=http://'.$addr.$_SERVER['REQUEST_URI'].'">';
    exit();
}

 
$DB_FILENAME = "/opt/catan/db/catan.sqlite";
$LINK_DIR = "links/";
$DEFAULT_LINK = "home.php";
		

$DB = new SQLite3($DB_FILENAME);
$DB->busyTimeout(10000);



/**
 * Are we logging out?
 */
if (isset($_GET['logout'])) {
	unset($_COOKIE["CATAN"]);
	setcookie("CATAN", null, -1, '/');

	// Strip logout and refresh page
	$uri = parse_str($_SERVER['QUERY_STRING'], $params);
	unset($params['logout']);
	$stripped_params = http_build_query($params, '', '&amp;');
	echo '<META HTTP-EQUIV=REFRESH CONTENT="0; URL=?'.$stripped_params.'">';
	exit;
}

/**
 * Is this our special status page?
 */
if (isset($_GET['l']) && $_GET['l'] == "status") {

	// Refresh every 10 seconds
	$uri = $_SERVER['QUERY_STRING'];
	echo '<META HTTP-EQUIV=REFRESH CONTENT="10; URL=?'.$uri.'">';
}

/**
 * Get all of the messages left for this user.
 * 
 * @param unknown $person_id
 */
function get_messages($person_id) {
	global $DB;
	
	$person_id = $DB->escapeString($person_id);
	
	// Perform our SQL Query
    /*
 	$sql = "SELECT * FROM db_person_messages 
 			JOIN db_submitter_info 
 			JOIN db_person_bio 
 			ON db_person_messages.submission_id=db_submitter_info.submission_id
 			AND db_person_messages.origin_node_id =db_submitter_info.origin_node_id
 			AND  db_submitter_info.submitter_id=db_person_bio.person_id
 			WHERE db_person_messages.person_id='$person_id'
 			ORDER BY db_submitter_info.timestamp DESC";
    */
 		
    $sql = "SELECT * 
            FROM db_person_messages AS messages
 			JOIN db_submitter_info AS sub
 			ON sub.submission_id=messages.submission_id
 			LEFT JOIN db_person_bio AS bio
 			ON bio.person_id=sub.submitter_id
 			WHERE messages.person_id='$person_id'
 			ORDER BY sub.timestamp DESC";
 	 			
 	$results = $DB->query($sql);
 	
 	return $results;
}


/**
 * Retreive all of the pictures associated with this person id
 * 
 * @param unknown $person_id
 * @return unknown
 */
function get_pictures($person_id) {
	global $DB;
	
	$person_id = $DB->escapeString($person_id);
	
	// Perform our SQL Query
	$sql = "SELECT * FROM db_pictures 
			JOIN db_person_pictures 
			JOIN db_submitter_info
		WHERE db_pictures.picture_id=db_person_pictures.picture_id
		AND db_pictures.origin_node_id=db_person_pictures.origin_node_id
		AND db_submitter_info.origin_node_id=db_person_pictures.origin_node_id
		AND db_submitter_info.submission_id=db_person_pictures.submission_id
		AND person_id = '$person_id'
		ORDER BY db_submitter_info.timestamp DESC";

	$results = $DB->query($sql);
	
	return $results;
}

/**
 * This function will query the database to receive all entries to a particular
 * field and filter to only return the most recent value in each field.
 * 
 * @param unknown $person_id
 * @param unknown $database
 * @return boolean|multitype:unknown
 */
function get_recent_fields($person_id, $database) {
	global $DB;
	
	$person_id = $DB->escapeString($person_id);
	$database = $DB->escapeString($database);
	
	// Perform our SQL Query
	$sql = "SELECT * FROM $database JOIN db_submitter_info 
			WHERE db_submitter_info.submission_id=$database.submission_id
			AND db_submitter_info.origin_node_id=$database.origin_node_id 
			AND person_id = '$person_id' 
			ORDER BY db_submitter_info.timestamp DESC";
	$results = $DB->query($sql);
	$rtn_array = Array();
	
// 	print "$sql<BR>";
	if (!$results->fetchArray()) {
		return false;
	} else {
	
		$results->reset();
		
		// Loop over all rows that are ordered by timestamp
		while ($row = $results->fetchArray()) {
			foreach ($row as $key => $value) {
				if (!array_key_exists($key, $rtn_array)) {
					$rtn_array[$key] = $value;
				}
				
				// Keep the first time we see each value as this will be the most recent
				if ($rtn_array[$key] == null && $value != null) {
					$rtn_array[$key] = $value;
				}
			}
		}
		
		return $rtn_array;
	}
}

function get_user_info($person_id) {
	global $DB;
	
	$person_id = $DB->escapeString($person_id);
	$sql = "SELECT * FROM db_person_bio
			WHERE person_id = '$person_id'";
	
// 	echo $sql;
	$results = $DB->query($sql);
	
// 	var_dump($results);
	return $results;
}


function get_cookie_info($cookie_value) {
	global $DB;
	$cookie_value = $DB->escapeString($cookie_value);
	$sql = "SELECT * FROM db_submitter_info JOIN db_catan_identity 
			ON db_catan_identity.submission_id=db_submitter_info.submission_id 
			WHERE db_submitter_info.cookie='$cookie_value' 
			ORDER BY db_submitter_info.timestamp DESC
			LIMIT 1";
	$results = $DB->query($sql);
	$result_array = $results->fetchArray();

	// If this cookie doesn't even exist, exit
	if (!$result_array)
		return false;
	
	// Lookup the person info for this person
	return get_user_info($result_array['person_id']);
}


function db_person_search($name_family, $name_given) {
	global $DB;
	
	$name_family = $DB->escapeString($name_family);
	$name_given = $DB->escapeString($name_given);
	$sql = "SELECT * FROM db_person_bio WHERE name_given LIKE '%$name_given%' and name_family LIKE '%$name_family%'";
	$results = $DB->query($sql);
	return $results;
}


if (isset($_COOKIE["CATAN"])) {
	$query_results = get_cookie_info($_COOKIE["CATAN"]);
	if (!$query_results) {
		$_SESSION['USER_INFO'] = $query_results;
	} else {
		$_SESSION['USER_INFO'] = $query_results->fetchArray();
	}
} else {
	$_SESSION['USER_INFO'] = false;
}


// Try to get our node information from the config
$conf_file = parse_ini_file("/opt/catan/conf/catan.conf");
?>
