package de.uni.trier.infsec.eVotingSystem.apps;


import static de.uni.trier.infsec.utils.Utilities.byteArrayToHexString;
import static de.uni.trier.infsec.eVotingSystem.core.Utils.out;
import static de.uni.trier.infsec.eVotingSystem.core.Utils.outl;

import java.awt.EventQueue;

import javax.swing.AbstractAction;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.GroupLayout;
import javax.swing.GroupLayout.Alignment;
import javax.swing.JScrollPane;
import javax.swing.UIManager;
import javax.swing.JTextField;
import javax.swing.JPasswordField;
import javax.swing.JLabel;
import javax.swing.LayoutStyle.ComponentPlacement;
import javax.swing.border.Border;
import javax.swing.border.TitledBorder;
import javax.swing.JButton;

import java.awt.BorderLayout;
import java.awt.GridLayout;

import javax.swing.BorderFactory; 

import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.StringSelection;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.AWTEvent;
import java.awt.CardLayout;
import java.awt.Color;
import java.awt.Cursor;

import javax.swing.SwingConstants;

import java.awt.Font;
import java.io.FileNotFoundException;
import java.io.IOException;

import de.uni.trier.infsec.eVotingSystem.bean.VoterID;
import de.uni.trier.infsec.eVotingSystem.core.Params;
import de.uni.trier.infsec.eVotingSystem.core.Voter;
import de.uni.trier.infsec.eVotingSystem.core.Voter.Error;
import de.uni.trier.infsec.eVotingSystem.parser.ElectionManifest;
import de.uni.trier.infsec.functionalities.digsig.*;
import de.uni.trier.infsec.functionalities.pkenc.*;
import de.uni.trier.infsec.utils.MessageTools;
import de.uni.trier.infsec.utils.Utilities;
import de.uni.trier.infsec.lib.network.NetworkClient;
import de.uni.trier.infsec.lib.network.NetworkError;

import javax.swing.JTextArea;

import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.Toolkit;





public class VoterApp extends JFrame {
	
	private static final long serialVersionUID = 1L;
	
	private JTextField fldVoterID;
	private JPasswordField fldPassword;
	private JLabel lblUserNotRegister;
	private JPanel center;
	private JPanel main;
	private JPanel north;
	private final static String LOGIN = "LOGIN";
	private final static String MAIN = "MAIN";
	private final static String REGISTRATION = "REGISTRATION";
	
	private final static String VOTE = "VOTE";
	private final static String ACCEPTED="ACCEPTED";
    private final static String REJECTED = "REJECTED";
  
	private JPanel ballot;
	private JTextArea textNonce;
	
	
	private JLabel lblRejectedReason = new JLabel("Rejected Reason");
	private JLabel lblCandidateSelected = new JLabel("Candidate Selected");
	private JLabel lblWait = new JLabel("Wait...");
	private JLabel lblVoterID = new JLabel("VoterID");
	private JLabel lblElectionMsg = new JLabel("Election Message");
	
	private JLabel lblGetCodeProblem;
	
	private JButton[] btnCandidates = new JButton[1];
	private JButton btnVote = new JButton();
	private VoteButton voteButtonAction;
	/*
	 * CORE FIELD
	 */
	private int voterID;
	private Voter voter;
	private Decryptor voter_decr;
	private Signer voter_sign;
	private byte[] serverResponse=null;
	private static ElectionManifest manifest;
	private Voter.ResponseTag responseTag;
	private Voter.Receipt receipt;
	//private static final int STORE_ATTEMPTS = 3; 
	// attempts to store a msg under a label in such a way that server and client counters are aligned

	private int selectedCandidate = -100;
	
	// STRING DISPLAYED FIELDS
		// login phase
	private final String lblCREDENTIALS = "Please enter";
	private final String lblVOTERID = "Your email: ";
	private final String lblPASSWORD = "Your code: ";
	private final String lblLOGIN = "Submit";
		// vote phase
	private final String lblYOURCHOICE = "Your Choice:";
	//FIXME: rephrase the messages 
	private final String lblACCEPTED = "<font color=\"green\">Your Vote has been collected properly!</font>";	// Vote Sent!
	private final String lblREJECTED = "<font color=\"red\">Your Vote has not been collected!</font>";			// Your Vote was not sent!
	private final String lblVOTEACCEPTED="Your <b>receipt</b> has been stored on your computer.<br><br>" +
	"After the election, please use your <b>Receipt ID</b> to make sure that your vote has been counted correctly.";
	private final String lblENDCOPY  = "to copy the <b>Receipt ID</b> to your computer's clipboard";

	private final String lblLOGOUT = "Finish";
	
	
	private static VoterApp frame;
	private JTextField fldEmail;
	private JTextField otpField;
	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		try {
			UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
		} catch (Throwable e) {
			e.printStackTrace();
		}
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					frame = new VoterApp();
					frame.setVisible(true);
					frame.setResizable(false);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	
	/**
	 * Create the frame.
	 */
	public VoterApp() {
		//setIconImage(Toolkit.getDefaultToolkit().getImage(UserGUI.class.getResource("/de/uni/trier/infsec/cloudStorage/cloud.png")));
		setTitle(AppParams.VOTERAPPNAME);
		//setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE | JFrame.DISPOSE_ON_CLOSE);
		setBounds(100, 100, 530, 700);
				// (530, 334);
		
		out("Getting election manifest...");
		manifest=AppUtils.retrieveElectionManifest();
		outl("OK");
		
		CardLayout cl = new CardLayout();
		getContentPane().setLayout(cl);
		
		
		// login Panel
		JPanel login = new JPanel();
		
		JLabel lblCredentials = new JLabel(lblCREDENTIALS);
		lblCredentials.setFont(new Font("Dialog", Font.BOLD, 15));
		
		JLabel lblVoterId = new JLabel(lblVOTERID);
		lblVoterId.setFont(new Font("Dialog", Font.BOLD, 14));
		fldVoterID = new JTextField();
		fldVoterID.setColumns(11);
		
		JLabel lblPassword = new JLabel(lblPASSWORD);
		lblPassword.setFont(new Font("Dialog", Font.BOLD, 14));
		fldPassword = new JPasswordField();
		fldPassword.setColumns(11);
		
		JButton btnLogin = new JButton(lblLOGIN);
		btnLogin.setFont(new Font("Dialog", Font.BOLD, 14));
		/*
		 * LOGIN!
		 */
		btnLogin.addActionListener(new Login());
		btnLogin.addKeyListener(new LoginPressed());
		
		lblUserNotRegister = new JLabel("");
		lblUserNotRegister.setFont(new Font("Dialog", Font.BOLD, 14));
		lblUserNotRegister.setHorizontalAlignment(SwingConstants.LEFT);
		lblUserNotRegister.setForeground(Color.RED);
		
		lblWait = new JLabel();
		lblWait.setHorizontalAlignment(SwingConstants.CENTER);
		
		JLabel lblTvote = new JLabel(AppParams.VOTERAPPNAME);
		lblTvote.setFont(new Font("Dialog", Font.BOLD | Font.ITALIC, 30));
		lblTvote.setHorizontalAlignment(SwingConstants.CENTER);
		
		GroupLayout gl_login = new GroupLayout(login);
		gl_login.setHorizontalGroup(
			gl_login.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_login.createSequentialGroup()
					.addGap(143)
					.addGroup(gl_login.createParallelGroup(Alignment.LEADING, false)
						.addComponent(lblPassword)
						.addComponent(lblVoterId, GroupLayout.PREFERRED_SIZE, 124, GroupLayout.PREFERRED_SIZE))
					.addPreferredGap(ComponentPlacement.RELATED, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
					.addGroup(gl_login.createParallelGroup(Alignment.LEADING, false)
						.addComponent(fldVoterID, 0, 0, Short.MAX_VALUE)
						.addComponent(fldPassword, GroupLayout.DEFAULT_SIZE, 114, Short.MAX_VALUE))
					.addGap(142))
				.addGroup(gl_login.createSequentialGroup()
					.addContainerGap()
					.addComponent(lblTvote, GroupLayout.DEFAULT_SIZE, 518, Short.MAX_VALUE)
					.addContainerGap())
				.addGroup(gl_login.createSequentialGroup()
					.addGap(50)
					.addGroup(gl_login.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_login.createSequentialGroup()
							.addGap(262)
							.addComponent(lblWait, GroupLayout.PREFERRED_SIZE, 69, GroupLayout.PREFERRED_SIZE))
						.addGroup(gl_login.createSequentialGroup()
							.addComponent(lblCredentials, GroupLayout.DEFAULT_SIZE, 232, Short.MAX_VALUE)
							.addGap(260))))
				.addGroup(gl_login.createSequentialGroup()
					.addGap(62)
					.addComponent(lblUserNotRegister, GroupLayout.PREFERRED_SIZE, 300, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.UNRELATED)
					.addComponent(btnLogin, GroupLayout.PREFERRED_SIZE, 93, GroupLayout.PREFERRED_SIZE)
					.addContainerGap(69, Short.MAX_VALUE))
		);
		gl_login.setVerticalGroup(
			gl_login.createParallelGroup(Alignment.TRAILING)
				.addGroup(gl_login.createSequentialGroup()
					.addGap(43)
					.addComponent(lblTvote, GroupLayout.PREFERRED_SIZE, 63, GroupLayout.PREFERRED_SIZE)
					.addGap(18)
					.addComponent(lblCredentials, GroupLayout.PREFERRED_SIZE, 25, GroupLayout.PREFERRED_SIZE)
					.addGap(52)
					.addGroup(gl_login.createParallelGroup(Alignment.BASELINE)
						.addGroup(gl_login.createSequentialGroup()
							.addGap(2)
							.addComponent(lblVoterId, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
						.addComponent(fldVoterID, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
					.addGap(35)
					.addGroup(gl_login.createParallelGroup(Alignment.BASELINE)
						.addGroup(gl_login.createSequentialGroup()
							.addGap(2)
							.addComponent(lblPassword, GroupLayout.DEFAULT_SIZE, 17, Short.MAX_VALUE))
						.addComponent(fldPassword, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
					.addGap(53)
					.addComponent(lblWait)
					.addGap(18)
					.addGroup(gl_login.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_login.createSequentialGroup()
							.addGap(31)
							.addComponent(lblUserNotRegister, GroupLayout.PREFERRED_SIZE, 88, GroupLayout.PREFERRED_SIZE))
						.addComponent(btnLogin, GroupLayout.PREFERRED_SIZE, 35, GroupLayout.PREFERRED_SIZE))
					.addGap(236))
		);
		login.setLayout(gl_login);
		
		
		
		
		// main windows panel
		main = new JPanel();
		
		JPanel registration = new JPanel();
		
		fldEmail = new JTextField();
		fldEmail.setFont(new Font("Dialog", Font.PLAIN, 20));
		fldEmail.setColumns(11);
		
		JLabel label_2 = new JLabel("sElect");
		label_2.setHorizontalAlignment(SwingConstants.CENTER);
		label_2.setFont(new Font("Dialog", Font.BOLD | Font.ITALIC, 30));
		
		JLabel lblPleaseEnterYour = new JLabel("Please enter your email address:");
		lblPleaseEnterYour.setFont(new Font("Dialog", Font.BOLD, 15));
		
		lblGetCodeProblem = new JLabel("");
		lblGetCodeProblem.setHorizontalAlignment(SwingConstants.LEFT);
		lblGetCodeProblem.setForeground(Color.RED);
		lblGetCodeProblem.setFont(new Font("Dialog", Font.BOLD, 14));
		
		JButton btnGetACode = new JButton("Get a code");
		btnGetACode.setFont(new Font("Dialog", Font.BOLD, 14));
		
		btnGetACode.addActionListener(new GetCode());
		btnGetACode.addKeyListener(new GetCodePressed());
		
		JLabel lblRegistrationPhase = new JLabel(manifest.title);
		lblRegistrationPhase.setFont(new Font("Dialog", Font.BOLD, 15));
		
		JLabel label = new JLabel(manifest.description);
		label.setFont(new Font("Dialog", Font.BOLD, 15));
		GroupLayout gl_registration = new GroupLayout(registration);
		gl_registration.setHorizontalGroup(
			gl_registration.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_registration.createSequentialGroup()
					.addGroup(gl_registration.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_registration.createSequentialGroup()
							.addGap(45)
							.addGroup(gl_registration.createParallelGroup(Alignment.TRAILING, false)
								.addGroup(gl_registration.createSequentialGroup()
									.addPreferredGap(ComponentPlacement.RELATED)
									.addGroup(gl_registration.createParallelGroup(Alignment.LEADING)
										.addComponent(label, GroupLayout.PREFERRED_SIZE, 439, GroupLayout.PREFERRED_SIZE)
										.addComponent(lblRegistrationPhase, GroupLayout.PREFERRED_SIZE, 439, GroupLayout.PREFERRED_SIZE)))
								.addGroup(gl_registration.createSequentialGroup()
									.addGroup(gl_registration.createParallelGroup(Alignment.TRAILING)
										.addComponent(btnGetACode, GroupLayout.PREFERRED_SIZE, 161, GroupLayout.PREFERRED_SIZE)
										.addComponent(fldEmail, GroupLayout.DEFAULT_SIZE, 440, Short.MAX_VALUE)
										.addComponent(lblPleaseEnterYour, Alignment.LEADING, GroupLayout.PREFERRED_SIZE, 301, GroupLayout.PREFERRED_SIZE)
										.addComponent(lblGetCodeProblem, Alignment.LEADING, GroupLayout.PREFERRED_SIZE, 300, GroupLayout.PREFERRED_SIZE))
									.addGap(485))))
						.addGroup(gl_registration.createSequentialGroup()
							.addGap(23)
							.addComponent(label_2, GroupLayout.PREFERRED_SIZE, 489, GroupLayout.PREFERRED_SIZE)))
					.addContainerGap(GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
		);
		gl_registration.setVerticalGroup(
			gl_registration.createParallelGroup(Alignment.TRAILING)
				.addGroup(gl_registration.createSequentialGroup()
					.addContainerGap()
					.addComponent(label_2, GroupLayout.PREFERRED_SIZE, 63, GroupLayout.PREFERRED_SIZE)
					.addGap(50)
					.addComponent(lblRegistrationPhase, GroupLayout.PREFERRED_SIZE, 25, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED, 31, Short.MAX_VALUE)
					.addComponent(label, GroupLayout.PREFERRED_SIZE, 47, GroupLayout.PREFERRED_SIZE)
					.addGap(77)
					.addComponent(lblPleaseEnterYour, GroupLayout.PREFERRED_SIZE, 25, GroupLayout.PREFERRED_SIZE)
					.addGap(18)
					.addComponent(fldEmail, GroupLayout.PREFERRED_SIZE, 34, GroupLayout.PREFERRED_SIZE)
					.addGap(61)
					.addComponent(btnGetACode, GroupLayout.PREFERRED_SIZE, 35, GroupLayout.PREFERRED_SIZE)
					.addGap(18)
					.addComponent(lblGetCodeProblem, GroupLayout.PREFERRED_SIZE, 88, GroupLayout.PREFERRED_SIZE)
					.addGap(88))
		);
		registration.setLayout(gl_registration);
		
		// add the two layout to the main
		getContentPane().add(registration, REGISTRATION);
		getContentPane().add(login, LOGIN);
		getContentPane().add(main, MAIN);
		
		main.setLayout(new BorderLayout(0, 0));
		// set the default option
		cl.show(getContentPane(), REGISTRATION);
		
		// North panel
		north = new JPanel();
		main.add(north, BorderLayout.NORTH);
		lblVoterID.setText("Insert your code:");
		
		otpField = new JTextField();
		otpField.setColumns(10);
		//labelField.setColumns(10);
		GroupLayout gl_north = new GroupLayout(north);
		gl_north.setHorizontalGroup(
			gl_north.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_north.createSequentialGroup()
					.addGap(24)
					.addGroup(gl_north.createParallelGroup(Alignment.LEADING)
						.addComponent(otpField, GroupLayout.PREFERRED_SIZE, 472, GroupLayout.PREFERRED_SIZE)
						.addComponent(lblVoterID))
					.addContainerGap(34, Short.MAX_VALUE))
		);
		gl_north.setVerticalGroup(
			gl_north.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_north.createSequentialGroup()
					.addContainerGap()
					.addComponent(lblVoterID)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(otpField, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
					.addContainerGap(GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
		);
		north.setLayout(gl_north);
		
		
		// Center panel
		center = new JPanel();
		main.add(center, BorderLayout.CENTER);
		CardLayout clCenter = new CardLayout(0, 0);
		center.setLayout(clCenter);
		
		JPanel votePanel = new JPanel();
		
		
		lblElectionMsg.setText("");
		lblElectionMsg.setFont(new Font("Dialog", Font.BOLD, 16));
		lblCandidateSelected.setText("");
		lblCandidateSelected.setForeground(Color.BLUE);
		lblCandidateSelected.setVerticalAlignment(SwingConstants.TOP);
		lblCandidateSelected.setHorizontalAlignment(SwingConstants.LEFT);
		lblCandidateSelected.setFont(new Font("Dialog", Font.BOLD, 16));
		
		ballot = new JPanel();
		
		JScrollPane ScrollBallot = new JScrollPane(ballot);
		//Border paneEdge = BorderFactory.createEmptyBorder(0,10,10,10);
		//Border loweredetched = BorderFactory.createEtchedBorder(EtchedBorder.LOWERED);
		Border blackline = BorderFactory.createLineBorder(Color.black);
        TitledBorder titledBorder = BorderFactory.createTitledBorder(blackline, "ballot");
        titledBorder.setTitleJustification(TitledBorder.RIGHT);
        titledBorder.setTitlePosition(TitledBorder.DEFAULT_POSITION);
        ScrollBallot.setBorder(titledBorder);
        
        
        // CREATE n BUTTONS AS NUMBER OF CANDIDATES
        int nCandidates=manifest.choicesList.length;
//        		.candidatesArray.length;
        ballot.setLayout(new GridLayout(nCandidates,1));
        btnCandidates = new JButton[nCandidates];
        
        
        for(int i=0;i<nCandidates; i++){
        	btnCandidates[i] = new JButton(new CandidateButton(manifest.choicesList[i], i, btnCandidates));
        	btnCandidates[i].setFont(new Font("Dialog", Font.BOLD, 14));
        	btnCandidates[i].setForeground(Color.BLACK);
        	//btnCandidates[i].setContentAreaFilled(false);
        	//btnCandidates[i].setOpaque(true);
        	/*
        	 * SELECT A CANDIDATE
        	 */
        	//btnCandidates[i].addActionListener(new CandidateSelected());
        	ballot.add(btnCandidates[i]);
        }
        /*
		 * VOTE!
		 */
        voteButtonAction = new VoteButton("Vote");
        btnVote = new JButton(voteButtonAction);
		btnVote.setFont(new Font("Dialog", Font.BOLD, 18));
		btnVote.setEnabled(false);
		
		JLabel lblYourChoce = new JLabel(lblYOURCHOICE);
		
        
		GroupLayout gl_votePanel = new GroupLayout(votePanel);
		gl_votePanel.setHorizontalGroup(
			gl_votePanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_votePanel.createSequentialGroup()
					.addContainerGap()
					.addGroup(gl_votePanel.createParallelGroup(Alignment.LEADING)
						.addComponent(lblElectionMsg, GroupLayout.PREFERRED_SIZE, 453, GroupLayout.PREFERRED_SIZE)
						.addGroup(gl_votePanel.createParallelGroup(Alignment.TRAILING, false)
							.addComponent(ScrollBallot, Alignment.LEADING, GroupLayout.PREFERRED_SIZE, 475, GroupLayout.PREFERRED_SIZE)
							.addGroup(gl_votePanel.createSequentialGroup()
								.addGroup(gl_votePanel.createParallelGroup(Alignment.LEADING)
									.addComponent(lblYourChoce)
									.addComponent(lblCandidateSelected, GroupLayout.PREFERRED_SIZE, 331, GroupLayout.PREFERRED_SIZE))
								.addPreferredGap(ComponentPlacement.RELATED, 49, Short.MAX_VALUE)
								.addComponent(btnVote, GroupLayout.PREFERRED_SIZE, 95, GroupLayout.PREFERRED_SIZE))))
					.addContainerGap(43, Short.MAX_VALUE))
		);
		gl_votePanel.setVerticalGroup(
			gl_votePanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_votePanel.createSequentialGroup()
					.addContainerGap()
					.addComponent(lblElectionMsg, GroupLayout.PREFERRED_SIZE, 50, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(ScrollBallot, GroupLayout.PREFERRED_SIZE, 428, GroupLayout.PREFERRED_SIZE)
					.addGap(18)
					.addGroup(gl_votePanel.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_votePanel.createSequentialGroup()
							.addComponent(lblYourChoce)
							.addPreferredGap(ComponentPlacement.RELATED)
							.addComponent(lblCandidateSelected, GroupLayout.DEFAULT_SIZE, 52, Short.MAX_VALUE))
						.addComponent(btnVote, GroupLayout.PREFERRED_SIZE, 46, GroupLayout.PREFERRED_SIZE))
					.addContainerGap())
		);
		votePanel.setLayout(gl_votePanel);
		
		JPanel acceptedPanel = new JPanel();
		
		
		
		JLabel lblVoteCorrect = new JLabel(html(lblACCEPTED));
		lblVoteCorrect.setForeground(UIManager.getColor("OptionPane.questionDialog.border.background"));
		lblVoteCorrect.setHorizontalAlignment(SwingConstants.CENTER);
		lblVoteCorrect.setFont(new Font("Dialog", Font.BOLD, 18));
		
		JLabel lblVoteAccepted = new JLabel(html(lblVOTEACCEPTED));
		lblVoteAccepted.setForeground(Color.BLACK);
		lblVoteAccepted.setHorizontalAlignment(SwingConstants.RIGHT);
		lblVoteAccepted.setFont(new Font("Dialog", Font.PLAIN, 14));
		
		
		textNonce = new JTextArea();
		textNonce.addMouseListener(new MouseAdapter() {
			public void mouseEntered(MouseEvent e) {
				setCursor(new Cursor(Cursor.TEXT_CURSOR));
			}
			public void mouseExited(MouseEvent e) {
				setCursor(new Cursor(Cursor.DEFAULT_CURSOR));
			}
		});
		textNonce.setEditable(false);
		textNonce.setWrapStyleWord(true);
		textNonce.setLineWrap(true);
		JScrollPane scrollNonce = new JScrollPane(textNonce);
		JLabel lblNonce = new JLabel(html("<b>Receipt ID:</b>"));
		scrollNonce.setColumnHeaderView(lblNonce);
		scrollNonce.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
		
		JLabel lblPress = new JLabel("Press");
		lblPress.setFont(new Font("Dialog", Font.PLAIN, 14));
		
		JButton btnCopy = new JButton(new CopyButton("Copy"));
		btnCopy.setText("Copy\n");
		
		JLabel lblEndCopy = new JLabel(html(lblENDCOPY));
		lblEndCopy.setFont(new Font("Dialog", Font.PLAIN, 14));
		
		GroupLayout gl_acceptedPanel = new GroupLayout(acceptedPanel);
		gl_acceptedPanel.setHorizontalGroup(
			gl_acceptedPanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_acceptedPanel.createSequentialGroup()
					.addContainerGap()
					.addGroup(gl_acceptedPanel.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_acceptedPanel.createSequentialGroup()
							.addComponent(lblVoteCorrect, GroupLayout.DEFAULT_SIZE, 506, Short.MAX_VALUE)
							.addContainerGap())
						.addGroup(gl_acceptedPanel.createSequentialGroup()
							.addGroup(gl_acceptedPanel.createParallelGroup(Alignment.LEADING)
								.addGroup(gl_acceptedPanel.createParallelGroup(Alignment.LEADING, false)
									.addComponent(lblVoteAccepted, GroupLayout.DEFAULT_SIZE, 445, Short.MAX_VALUE)
									.addComponent(scrollNonce, GroupLayout.PREFERRED_SIZE, 403, GroupLayout.PREFERRED_SIZE))
								.addGroup(gl_acceptedPanel.createSequentialGroup()
									.addComponent(lblPress)
									.addPreferredGap(ComponentPlacement.RELATED)
									.addComponent(btnCopy, GroupLayout.DEFAULT_SIZE, 106, Short.MAX_VALUE)
									.addPreferredGap(ComponentPlacement.UNRELATED)
									.addComponent(lblEndCopy, GroupLayout.DEFAULT_SIZE, 291, Short.MAX_VALUE)))
							.addGap(51))))
		);
		gl_acceptedPanel.setVerticalGroup(
			gl_acceptedPanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_acceptedPanel.createSequentialGroup()
					.addContainerGap()
					.addComponent(lblVoteCorrect, GroupLayout.PREFERRED_SIZE, 96, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblVoteAccepted, GroupLayout.PREFERRED_SIZE, 96, GroupLayout.PREFERRED_SIZE)
					.addGap(22)
					.addComponent(scrollNonce, GroupLayout.PREFERRED_SIZE, 103, GroupLayout.PREFERRED_SIZE)
					.addGap(58)
					.addGroup(gl_acceptedPanel.createParallelGroup(Alignment.BASELINE)
						.addComponent(lblEndCopy, GroupLayout.PREFERRED_SIZE, 56, GroupLayout.PREFERRED_SIZE)
						.addComponent(btnCopy)
						.addComponent(lblPress))
					.addContainerGap(150, Short.MAX_VALUE))
		);

		acceptedPanel.setLayout(gl_acceptedPanel);
		
		/*
		 * If you want to have the signature/innerballot JTextArea comment the code below and uncomment the code above
		 */
		
		/*textSignature = new JTextArea();
		textSignature.addMouseListener(new MouseAdapter() {
			public void mouseEntered(MouseEvent e) {
				setCursor(new Cursor(Cursor.TEXT_CURSOR));
			}
			public void mouseExited(MouseEvent e) {
				setCursor(new Cursor(Cursor.DEFAULT_CURSOR));
			}
		});
		textSignature.setEditable(false);
		textSignature.setWrapStyleWord(true);
		textSignature.setLineWrap(true);
		JScrollPane scrollSignature = new JScrollPane(textSignature);
		scrollSignature.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
		
		//JLabel lblSign = new JLabel(html("<b>Signed Acknowledgment:</b>"));
		JLabel lblSign = new JLabel(html("<b>Encrypted Ballot:</b>"));
		scrollSignature.setColumnHeaderView(lblSign);
		
		GroupLayout gl_acceptedPanel = new GroupLayout(acceptedPanel);
		gl_acceptedPanel.setHorizontalGroup(
			gl_acceptedPanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_acceptedPanel.createSequentialGroup()
					.addContainerGap()
					.addGroup(gl_acceptedPanel.createParallelGroup(Alignment.TRAILING, false)
						.addComponent(scrollNonce, Alignment.LEADING)
						.addGroup(Alignment.LEADING, gl_acceptedPanel.createParallelGroup(Alignment.LEADING, false)
							.addComponent(lblVoteCorrect, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
							.addComponent(lblVoteAccepted, GroupLayout.DEFAULT_SIZE, 445, Short.MAX_VALUE))
						.addComponent(scrollSignature, Alignment.LEADING, GroupLayout.DEFAULT_SIZE, 445, Short.MAX_VALUE))
					.addContainerGap(73, Short.MAX_VALUE))
		);
		gl_acceptedPanel.setVerticalGroup(
			gl_acceptedPanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_acceptedPanel.createSequentialGroup()
					.addContainerGap()
					.addComponent(lblVoteCorrect, GroupLayout.PREFERRED_SIZE, 96, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(lblVoteAccepted, GroupLayout.PREFERRED_SIZE, 96, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED, 22, Short.MAX_VALUE)
					.addComponent(scrollNonce, GroupLayout.PREFERRED_SIZE, 103, GroupLayout.PREFERRED_SIZE)
					.addPreferredGap(ComponentPlacement.RELATED)
					.addComponent(scrollSignature, GroupLayout.PREFERRED_SIZE, 103, GroupLayout.PREFERRED_SIZE)
					.addGap(55))
		);

		acceptedPanel.setLayout(gl_acceptedPanel);*/
		
		
		
		JPanel rejectedPanel = new JPanel();
		
		JLabel lblRejected=new JLabel(html(lblREJECTED));
		lblRejected.setHorizontalAlignment(SwingConstants.CENTER);
		lblRejected.setFont(new Font("Dialog", Font.BOLD, 18));
		
		
		
		center.add(votePanel, VOTE);
		center.add(acceptedPanel, ACCEPTED);
		
		center.add(rejectedPanel, REJECTED);
		GroupLayout gl_rejectedPanel = new GroupLayout(rejectedPanel);
		gl_rejectedPanel.setHorizontalGroup(
			gl_rejectedPanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_rejectedPanel.createSequentialGroup()
					.addGroup(gl_rejectedPanel.createParallelGroup(Alignment.LEADING)
						.addGroup(gl_rejectedPanel.createSequentialGroup()
							.addGap(32)
							.addComponent(lblRejectedReason, GroupLayout.PREFERRED_SIZE, 436, GroupLayout.PREFERRED_SIZE))
						.addGroup(gl_rejectedPanel.createSequentialGroup()
							.addContainerGap()
							.addComponent(lblRejected, GroupLayout.DEFAULT_SIZE, 506, Short.MAX_VALUE)))
					.addContainerGap())
		);
		gl_rejectedPanel.setVerticalGroup(
			gl_rejectedPanel.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_rejectedPanel.createSequentialGroup()
					.addGap(68)
					.addComponent(lblRejected)
					.addGap(77)
					.addComponent(lblRejectedReason, GroupLayout.PREFERRED_SIZE, 171, GroupLayout.PREFERRED_SIZE)
					.addContainerGap(266, Short.MAX_VALUE))
		);
		rejectedPanel.setLayout(gl_rejectedPanel);
		
		
		// South panel
		JPanel south = new JPanel();
		main.add(south, BorderLayout.SOUTH);
		
		JButton btnLogOut = new JButton(lblLOGOUT);
		
		btnLogOut.addActionListener(new Logout());
		btnLogOut.addActionListener(new CloseTheApp());
		
		GroupLayout gl_south = new GroupLayout(south);
		gl_south.setHorizontalGroup(
			gl_south.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_south.createSequentialGroup()
					.addContainerGap()
					.addComponent(btnLogOut)
					.addContainerGap(348, Short.MAX_VALUE))
		);
		gl_south.setVerticalGroup(
			gl_south.createParallelGroup(Alignment.LEADING)
				.addGroup(gl_south.createSequentialGroup()
					.addComponent(btnLogOut)
					.addContainerGap(GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
		);
		south.setLayout(gl_south);
	}
	
	
	/*
	 * LISTENERS
	 */
	private class GetCodePressed extends KeyAdapter{
		public void keyPressed(KeyEvent e) {
	         if(e.getKeyCode() == KeyEvent.VK_ENTER) {
	              onLoginPress(e);
	         }
	    }
	}
	private class GetCode implements ActionListener {
		public void actionPerformed(ActionEvent ev) {
			onGetCodePress(ev);
		}
	}
	
	private void onGetCodePress(AWTEvent ev){
		if(fldEmail.getText().length()==0){
			lblGetCodeProblem.setText("<html>Mail not inserted!</html>");
			return;
		}
		String email=fldEmail.getText();
		boolean allowedVoter=false;
		for(VoterID vid: manifest.votersList)
			if(allowedVoter=vid.email.equals(email))
				break;
		if(!allowedVoter){
			lblGetCodeProblem.setText(html("Improper Mail inserted"));
			return;
		}
		
		
		setupVoter(email);
		byte[] otpReq = voter.createOTPRequest();
		// Send the ballot:
		out("Sending the OTP request to the server...");
		try {
			
			serverResponse = NetworkClient.sendRequest(otpReq, 
					manifest.collectingServer.uri.hostname, 
					manifest.collectingServer.uri.port);
		} catch (NetworkError e) {
			outl("OTP request: networkError");
			e.printStackTrace();
		}
		outl("OK");
		Voter.ResponseTag respTag=null;
		try {
			respTag = voter.validateResponse(serverResponse);
		} catch (Error e) {
			outl("Vote [candidate <int>]: voteError");
			e.printStackTrace();
		}
		if (respTag != Voter.ResponseTag.OTP_REQUEST_ACCEPTED){
			lblGetCodeProblem.setText(html("Something went wrong"));
			return;
		}
		else {
			CardLayout cl = (CardLayout) getContentPane().getLayout();
			cl.show(getContentPane(), MAIN);
		}
			
	}
	
	
	
	
	private class LoginPressed extends KeyAdapter{
		public void keyPressed(KeyEvent e) {
	         if(e.getKeyCode() == KeyEvent.VK_ENTER) {
	              onLoginPress(e);
	         }
	    }
	}
	
	private class Login implements ActionListener {
		public void actionPerformed(ActionEvent ev) {
			onLoginPress(ev);
		}
	}
	
	private void onLoginPress(AWTEvent ev){
//		if(fldVoterID.getText().length()==0){
//			lblUserNotRegister.setText("<html>User ID field empty!<br>Please insert a valid ID number of a previously registered user.</html>");
//			return;
//		}
//		
//		try{
//			voterID = Integer.parseInt(fldVoterID.getText());
//			if(voterID<0)
//				throw new NumberFormatException();
//		} catch (NumberFormatException e){
//			outl("'" + fldVoterID.getText() + "' is not a proper userID!\nPlease insert the ID number of a previously registered user.");
//			lblUserNotRegister.setText("<html>'" + fldVoterID.getText() + "' is not a proper userID!<br>Please insert the ID number of a registered user.</html>");
//			return;
//		}
//		
//		
//		lblUserNotRegister.setText("");
//		lblWait.setText("Wait..."); //FIXME: it doesn't work!
//		
//		JPanel loginPanel = (JPanel) ((JButton)ev.getSource()).getParent();
//		//lblWait.paintImmediately(loginPanel.getVisibleRect());
//		loginPanel.paintImmediately(loginPanel.getVisibleRect());
//		
//		boolean voterRegistered=false;
//		try {
//			setupVoter(voterID);
//			voterRegistered=true;
//		} catch (FileNotFoundException e){
//			outl("User " + voterID + " not registered!\nType \'UserRegisterApp <user_id [int]>\' in a terminal to register him/her.");
//			lblUserNotRegister.setText("<html>User " + voterID + " not registered!<br>Please register yourself before log in.</html>");
//		} catch (IOException e){
//			outl("IOException occurred while reading the credentials of the user!");
//			lblUserNotRegister.setText("IOException occurred while reading the credentials of the user!");
//		} catch (RegisterSig.PKIError | RegisterEnc.PKIError e){
//			outl("PKI Error occurred: perhaps the PKI server is not running!");
//			lblUserNotRegister.setText("<html>PKI Error:<br> perhaps the PKI server is not running!</html>");
//		} catch (NetworkError e){
//			//FIXME: java.net.ConnectException when the PKIServer is not running!
//			outl("Network Error occurred while connecting with the PKI server: perhaps the PKI server is not running!");
//			lblUserNotRegister.setText("<html>Network Error occurred:<br> perhaps the PKI server is not running!</html>");
//		} finally{
//			lblWait.setText("");
//		}
//		if(voterRegistered){
//			fldVoterID.setText("");
//			//setTitle("Voter " + voterID + " - " + AppParams.APPNAME);
//			
//			//FIXME: it does not work
//			//getContentPane().setSize(530,600);
//			
//			CardLayout cl = (CardLayout) getContentPane().getLayout();
//			cl.show(getContentPane(), MAIN);
//			//getContentPane().setVisible(true);
//			
//		}
//		lblVoterID.setText("<html>" +  lblVOTERID + "<strong>" + voterID + "</strong></html>");
//		lblElectionID.setText(new String(manifest.electionID));
//		lblElectionMsg.setText("<html>" +  manifest.headline + "</html>");
	}
	
	private class CloseTheApp implements ActionListener{
		public void actionPerformed(ActionEvent e) {
			destroyConfidentialInfo();
			frame.dispose();
		}
	}
	
	private class Logout implements ActionListener {
		public void actionPerformed(ActionEvent e) {
			
			lblUserNotRegister.setText("");
			lblCandidateSelected.setText("");
			lblRejectedReason.setText("");
			for(int i=0;i<btnCandidates.length;i++)
				btnCandidates[i].setForeground(Color.BLACK);
			textNonce.setText("");
			//textSignature.setText("");
			
			CardLayout centerCl = (CardLayout) center.getLayout();
			centerCl.show(center, VOTE);
			
			CardLayout cl = (CardLayout) getContentPane().getLayout();
			cl.show(getContentPane(), LOGIN);
			
			destroyConfidentialInfo();
			setTitle(AppParams.VOTERAPPNAME);
		}
	}
	private void destroyConfidentialInfo(){
		selectedCandidate=-100;
		
		voter_decr=null;
		voter_sign=null;
		voter=null;
		responseTag=null;
		receipt=null;
	}
	
	
	private class CandidateButton extends AbstractAction {
		private JButton[] btnCandidates;
		private int candidateNumber;
		
		public CandidateButton(String name, int candidateNumber, JButton[] btnCandidates){
			super(name);
			this.candidateNumber=candidateNumber;
			this.btnCandidates=btnCandidates;
		}
		
		public void actionPerformed(ActionEvent ev){
			JButton btnSelected= (JButton) ev.getSource();
			btnSelected.setForeground(Color.BLUE);
			//FIXME: it does not work
					// btnSelected.setFont(new Font("Dialog", Font.BOLD, 30));
			btnSelected.repaint();
			// btnCandidates[candidateNumber].setBackground(Color.GREEN);
			for(int i=0;i<btnCandidates.length;i++)
				if(!btnCandidates[i].equals(btnSelected)){
//					selectedCandidate=i;
//				} else{
					btnCandidates[i].setForeground(Color.BLACK);
					//FIXME: it does not work 
							// btnSelected.setFont(new Font("Dialog", Font.BOLD, 14));
							//	btnCandidates[i].repaint();
				}
			selectedCandidate=candidateNumber;
			outl("Candidate Selected: " + selectedCandidate);
			
			btnVote.setEnabled(true);
			lblCandidateSelected.setText(html(manifest.choicesList[candidateNumber]));
			
			
			
		}
	}
	
	
	private class VoteButton extends AbstractAction {
		public VoteButton(String name){
			super(name);
		}
		public void actionPerformed(ActionEvent ev){
			if(selectedCandidate<0 || selectedCandidate>=manifest.choicesList.length)
				return; // no valid candidate has been selected
			boolean isNull=false;
			String otp=null;
			try{
				otp=otpField.getText();
			} catch (NullPointerException e){
				isNull=true;	
			}
			if(isNull || otp.equals("")) return;
				
			// Create a ballot;
			//TODO: comment this line and uncomment the other after testing
			out("Creating a ballot with candidate number " + selectedCandidate + "...");
			//outl("Creating the ballot...");
			byte[] ballot = voter.createBallot(selectedCandidate, Utilities.hexStringToByteArray(otp));
			outl("OK");
			
			// Send the ballot:
			out("Sending the ballot to the server...");
			//TODO: create another thread
			try {
				serverResponse = 
						NetworkClient.sendRequest(ballot, 
								manifest.collectingServer.uri.hostname, 
								manifest.collectingServer.uri.port);
			} catch (NetworkError e) {
				// TODO Auto-generated catch block
				// TODO: manage the app so that the vote is not colleted in this case
				outl("Vote [candidate <int>]: networkError");
				e.printStackTrace();
			}
			outl("OK");
			
			// Validate the server's response:
			try {
				responseTag = voter.validateResponse(serverResponse);
			} catch (Error e) {
				outl("response validation for voting: voteError");
				e.printStackTrace();
			}
			outl("Response of the server: " + responseTag);
			
			CardLayout cl = (CardLayout)(center.getLayout());
			if (responseTag == Voter.ResponseTag.VOTE_COLLECTED) {
				// Output the verification data:
				Voter.Receipt receipt = voter.getReceipt();
				outl("RECEIPT:");
				outl("    nonce = " + byteArrayToHexString(receipt.nonce));
				outl("    inner ballot = " + byteArrayToHexString(receipt.innerBallot));
				if (receipt.serverSignature != null)
					outl("    server's signature = " + byteArrayToHexString(receipt.serverSignature));
				
				// Store the receipt:
				String receipt_fname = AppParams.RECEIPT_file + voterID + ".msg"; 
				try {
					AppUtils.storeAsFile(receipt.asMessage(), receipt_fname);
				} catch (IOException e) {
					outl("Vote(candidate <int>): IOException");
					e.printStackTrace();
				}
				textNonce.setText(byteArrayToHexString(receipt.nonce));
				//textSignature.setText(byteArrayToHexString(receipt.innerBallot));
				//textSignature.setText(byteArrayToHexString(receipt.serverSignature));
				cl.show(center, ACCEPTED);
				main.remove(north);
				
			}
			else{
				String rejectedReason="";
				switch(responseTag){
				case INVALID_ELECTION_ID:
					rejectedReason += "Invalid election identifier.";
					break;
				case ELECTION_OVER:
					rejectedReason += "The voting phase is over.";	
					break;
				case ALREADY_VOTED:
					rejectedReason += "You have already voted with a different " +
							"ballot which has been collected properly.";	
					break;
//				case INVALID_VOTER_ID: //FIXME: do we still need this enum?
//					rejectedReason += "Your identifier number is incorrect";
//					break;
				default:
					rejectedReason += "I do not know the reason that your vote " +
							"has not been collected. You should try asking a polling official!";
				}
				lblRejectedReason.setText(html(rejectedReason));
				lblRejectedReason.setFont(new Font("Dialog", Font.PLAIN, 14));
				cl.show(center, REJECTED);
				main.remove(north);
			}
			 
		}					
	}
	
	private class CopyButton extends AbstractAction{
		public CopyButton(String name){
			super(name);
		}
		public void actionPerformed(ActionEvent ev){
			// copy the unselected text in the JTextArea textNonce to the clipboard
			StringSelection stringSelection = new StringSelection (textNonce.getText());
			Clipboard clpbrd = Toolkit.getDefaultToolkit().getSystemClipboard();
			clpbrd.setContents(stringSelection, null);
		}
	}
	
	private void setupVoter(String email){
		// Create the voter:
		out("Setting up the voter...");
		byte[] id = Utilities.stringAsBytes(email);
		voter = new Voter(id, manifest);
		outl("OK");
	}

	
	// UTILS methods
	private static String html(String s){
		return "<html>" + s + "</html>";
	}
}

