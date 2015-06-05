<?php
$name_given = $_GET['name_given'];
$name_family = $_GET['name_family'];

$results = db_person_search($name_family, $name_given);

if (!$results->fetchArray()) { 
	echo '<h2 align="center">No results found.</h2>';
} else {
	$results->reset();
	echo '<table id="tbl_search">';
	echo '<tr>';
	echo '<th>Family Name</th>';
	echo '<th>Given Name</th>';
	echo '<th>Sex</th>';
	echo '<th>Age</th>';
	echo '</tr>';
	while ($row = $results->fetchArray()) {
		
	     echo '<tr class="clickableRow" href="?l=profile&pid='.$row['person_id'].'">';
	     echo "<td>".$row['name_family']."</td>";
	     echo "<td>".$row['name_given']."</td>";
	     echo "<td>".$row['sex']."</td>";
	     echo "<td>".$row['age']."</td>";
	     echo '</tr>';
	     
     
	}
	echo '</table>';
}

echo '<div style="text-align:center;">';
echo "<a href=\"?l=new_person&name_given=$name_given&name_family=$name_family\">Add <b><i>$name_given $name_family</i></b> to database.</a>";
echo '</div>';
?>