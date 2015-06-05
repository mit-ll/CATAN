<?php 
/**
 * This is just a simple funciton to ensure that we have consistent output.
 * 
 * @param unknown $result_array
 * @param unknown $field
 */
function output_field($result_array, $field) {
	global $USER_IDENTIFIED;
	if ($result_array && $result_array[$field])
		return $result_array[$field];
	else if ($USER_IDENTIFIED)
		return '<input type="text" name="'.$field.'" />';
	else 
		return '';
}

// First search for this person in our database.
$person_id = $_GET['pid'];
$results = get_user_info($person_id);

if (!$USER_IDENTIFIED) {
?>
<div id="identify_form">
<form class="identify_form" method="post" enctype="multipart/form-data" action="/cgi-bin/catan_script.cgi">
<!-- Hidden inputs -->
	<input id="geo_location" type="hidden" name="submitter_gps" value="" />
	<input id="user_is_submitter" type="hidden" name="user_is_submitter" value="1" />
	<input id="person_id" type="hidden" name="person_id" value="<?php 
	echo $person_id; ?>" />
	<input type="submit" value="This is me" />
</form>
</div>
<?php
} else if ($USER_IDENTIFIED && $_SESSION['USER_INFO']['person_id'] == $person_id) {
	echo '<div style="text-align:center;"><span class="submit"><a href="'.$_SERVER['REQUEST_URI'].'&logout=1">I am not this person.</a></span></div>';
}


if (!$results->fetchArray()) {
	echo '<h2 align="center">Person not found.</h2>';
} else {
	
	$results->reset();
	$result_array = $results->fetchArray(SQLITE3_ASSOC);
	
	// Extract all of our data from the appropriate databases
	$contact_info = get_recent_fields($person_id,"db_person_contact");
	$description = get_recent_fields($person_id,"db_person_description");
// 	$location = get_recent_fields($person_id,"db_person_location");
// 	$status = get_recent_fields($person_id,"db_person_status");
	$pictures = get_pictures($person_id);
	$messages = get_messages($person_id);
	?>
	<form class="profile_form" method="post" enctype="multipart/form-data" action="/cgi-bin/catan_script.cgi">
	<div class="profile_table">
	
		<!-- Hidden inputs -->
		<input id="geo_location" type="hidden" name="submitter_gps" value="" />
		<input id="person_id" type="hidden" name="person_id" value="<?php 
		echo $person_id; ?>" />
		
		<?php
		// Add the submitter id
		if ($_SESSION['USER_INFO']) {
			echo '<input id="submitter_id" type="hidden" name="submitter_id" value="'.$_SESSION['USER_INFO']['person_id'].'">';
 		}
		?>
		<div class="profile_title">Identifying Information</div>
		<div class="profile_section">
			<span class="profile_label">Family Name:</span>
			<span class="profile_value"><?php echo $result_array['name_family'] ?></span>
		</div>
		<div class="profile_section">
			<span class="profile_label">Given Name:</span>
			<span class="profile_value"><?php echo $result_array['name_given'] ?></span>
		</div>
		<div class="profile_section">
			<span class="profile_label">Sex:</span>
			<span class="profile_value"><?php echo $result_array['sex'] ?></span>
		</div>
		<div class="profile_section">
			<span class="profile_label">Age:</span>
			<span class="profile_value"><?php echo $result_array['age'] ?></span>
		</div>
	    
	    <div class="profile_title">Description</div>
		<div class="profile_section">
			
			<span class="profile_label">Description:</span>
			<span class="profile_value">
			<?php 
			if ($USER_IDENTIFIED)
				echo '<textarea rows="4" name="person_description">';
			if ($description)
				echo $description['person_description'];
			if ($USER_IDENTIFIED)
				echo '</textarea>';
			?>
			</span>
		</div>
	    
	    <div class="profile_title">Address</div>
	    <?php 
	    $contact_array = Array("Street name:" => "street",
	    						"Neighborhood:" => "neighborhood",
	    						"State:" => "state",
	    						"ZIP:" => "zip",
	    						"Country:" => "country",
	    						"Phone:" => "phone",
	    						"E-mail:" => "email");
	    foreach ($contact_array as $key => $value) {
		echo '

		<div class="profile_section">
			
			<span class="profile_label">'.$key.'</span>
			<span class="profile_value">'.output_field($contact_info, $value).'</span>
		</div>';
		}
		?>
    	
		
		<div class="profile_title">Picture(s)</div>
		<?php 
		echo '<div class="profile_section" style="text-align:center;">';
		if ($pictures->fetchArray()) {
			$pictures->reset();
			
			
			
			while ($row = $pictures->fetchArray()) {
				echo '<div class="imageBox">';
				echo '<img src="data:image/jpeg;base64,'.base64_encode($row['picture_data']).'">';
				echo '<div class="imageDescription">';
				echo $row['picture_description'];
				echo "</div></div>";
			}
	
		} else {
			echo "<i>No pictures have been uploaded.</i>";
		}
		echo '</div>';
		
		
		if ($USER_IDENTIFIED) {
		?>
		<div class="profile_section">
			<span class="profile_label">Picture:</span>
			<span class="profile_value">
				<input type="file" name="picture_file">
			</span>
		</div>
		<div class="profile_section">
			<span class="profile_label">Description:</span>
			<span class="profile_value">
				<input type="text" name="picture_description">
			</span>
		</div>
		
		<div style="text-align:center;font-size:20pt;padding:5px;">
			<input type="submit" name="submit" value="Update profile">
		</div>
		<?php 
		}
		?>
	
	</div>
	
	
	<?php 
	if ($messages->fetchArray()) {
		$messages->reset();
		
		echo '<div id="person_messages">';
		echo '<div class="message_title">Notes</div>';
		while ($row = $messages->fetchArray()) {
			
			echo '<div class="message_item">';
			
			if ($row['status']) {
				$status_text = Array(
						'information_sought' => "Seeking information",
						'is_note_author' => "Self reported",
						'believed_alive' => "Believed to be alive",
						'believed_missing' => "Believed to be missing");
			
				echo '<div class="message_status">';
				// Report human-readable status (Not a bug)
				if (array_key_exists($row['status'],$status_text)) {
					echo $status_text[$row['status']];
				} else {
					echo $row['status'];
				}
				echo '</div>';
			}
			
			if ($row['person_message']) {
				echo '<div class="message_content">';
				echo $row['person_message'];
				echo '</div>';
			}
			
			if ($row['status_location']) {
				echo '<div class="message_location">
				<span class="message_label">Last known location was <b>';
				echo $row['status_location'];
				echo '</b></div>';
			}

			
			echo '<div class="message_header">';
			echo 'Submitted by ';
			echo '<a href="?l=profile&person_id='.$row['submitter_id'].'">';
			echo $row['name_given'].' '.$row['name_family'];
			echo '</a>';
			echo ' on ';
			echo date("F j, Y, g:i a",$row['timestamp']);
			echo '</div>';
			echo '</div>';
// 			var_dump($row);
		}
		echo '</div>';
	} else {
	    echo '<div id="person_messages">';
		echo '<div class="message_title">Notes</div>';
		echo '<div class="message_content">';
	    echo 'No Messages';// for ' . $person_id;
	    echo '</div>';
	    echo '</div>';
	}
	
	if ($USER_IDENTIFIED) {
	?>
	<div class="profile_table" id="status_table">
		<div class="profile_title">Tell us the status of this person</div>
		<div class="profile_section">
			<span class="profile_label">Status:</span>
			<span class="profile_value">
			<select id="status" name="status">
	          
	            <option value="">
	              Unspecified
	            </option>
	          $status['status']
	            <option value="information_sought">
	              I am seeking information
	            </option>
	          
	            <option value="is_note_author">
	              I am this person
	            </option>
	          
	            <option value="believed_alive">
	              I have received information that this person is alive
	            </option>
	          
	            <option value="believed_missing">
	              I have reason to think this person is missing
	            </option>
	          
	        </select>
			</span>
		</div>
		<div class="profile_section">
			<span class="profile_label">Last know location:</span>
			<span class="profile_value">
				<textarea rows="4" name="status_location"></textarea>
			</span>
		</div>
		
		<div class="profile_section">
			<span class="profile_label">Message:</span>
			<span class="profile_value">
				<textarea rows="4" name="person_message"></textarea>
			</span>
		</div>
		
		<div class="profile_section">
			<span class="profile_label">Relation to person:</span>
			<span class="profile_value">
				<input type="text" name="relationship" />
			</span>
		</div>
		
		<div style="text-align:center;font-size:20pt;padding:5px;">
			<input type="submit" name="submit" value="Submit a note.">
		</div>
	</div>
	<?php 
	}
	?>
	</form>
<?php 
}
?>
