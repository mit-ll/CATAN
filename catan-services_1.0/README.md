© 2015 Massachusetts Institute of Technology

# Meeting Notes (Communication)
	Application Layer:
	Defines basic type of messages (and associated communication path):

	PersonFinder (Node -> GW )
	Bulletins  (GW -> All)
	Help Message (Node -> GW)
	User Query  (Node A -> GW -> Node A)
	User2User Message (Node A -> GW -> Node B)

	Transport Layer:
	Fields that would be used in the transport layer header:

	Source ID
	Destination ID
	Message ID
	Message Type (Data, Ack,..)
	Via/Path: ? (or does this belong to the network layer?)

	Network Layer:
	Discussed various concepts for routing packets, in particular when to flood and when to specify particular routes.  The link layer will be implemented by our node software.  Lower layers will be handled by the a back-end link software.

	A concept for a network protocol that we discussed was the following:

	The gateway (GW) periodically broadcasts "GW Announcement" packets which are rebroadcast by each receiving node after incrementing a hop count that is initialized to zero by the gateway.  Each node tracks the other nodes from which it heard a "GW Announcement".  The neighbor with the lowest hop count becomes the "Best GW Path Node" for that node.

	When a node receives a packet destined for the GW, it looks up the "Best GW Path Node" and forwards the packet to that node, via the link layer, with its own ID appended to a "Via" field.  The receiving packet repeats the process until the packet reaches the GW.  Note each node only needs to store a single row in it's "routing table", though we may wish to store a secondary backup path. 

	When the GW sends a response (whether an ACK or other data) back to a node it uses the Via field in the original request to specify a specific route that it should take through any intermediate nodes, avoiding the need to do a "layer-3" broadcast.
	    
	Link Layer (Back-end):

	Current options being considered: 
	    ARC platform (Gr. 42)
	    AX.25 (APRS)
