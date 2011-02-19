;;; ditto.el --- Emacs interface to Ditto issue tracking system 

;; this is heavily based on ditz.el, and most functionality is not complete yet

;; Customizable variables
(defcustom ditto-program "ditto"
  "Ditto command"
  :type 'string
  :group 'ditto)

(defcustom ditto-issue-directory "bugs"
  "Default directory name in which issues are stored.

You must set it some value according with your environment when
you use automatic finding described below."
  :type 'string
  :group 'ditto)

(defcustom ditto-find-issue-directory-automatically-flag nil
  "If non-nil, issue directory will be found automatically in
directories from the current one toward the root. Otherwise, you
must set it from minibuffer."
  :type 'boolean
  :group 'ditto)

;; Constant variables
(defconst ditto-issue-id-regex "^...\\([^ ]*\\).*$"
  "Regex for issue id.")

;;(defconst ditto-issue-id-regex-in-issue "^Issue \\([^ ]*-[^ ]*\\)"
(defconst ditto-issue-id-regex-in-issue "^Issue \\(.*\\)"
  "Regex for issue when showing it")

(defconst ditto-issue-guid-regex "^[_ ]+[^:]+: \\([^:\n]+\\) :.*$"
  "Regex for issue guid.")

(defconst ditto-release-name-regex "^\\(\\)\\(.*\\)$"
  "Regex for release id.")

(defconst ditto-feature-name-regex "^:Feature: \\(Version \\)?\\([^\n ]+\\) *.*$"
  "Regex for feature id.")

(defconst ditto-issue-description-regex "^.*: (.*) \\(.*\\)$"
  "Regex for issue description.")

;; Commands
(defun ditto-init ()
  "Initialize ditto issues."
  (interactive)
  (ditto-call-process "init" nil "pop"))

(defun ditto-html ()
  "Generate html files of issues."
  (interactive)
  (ditto-call-process "html" nil "display"))

(defun ditto-add-release ()
  "Add a new release."
  (interactive)
  (ditto-call-process "add-release" nil "pop"))

(defun ditto-add-feature ()
  "Add a new feature."
  (interactive)
  (ditto-call-process "add-feature" nil "pop"))

(defun ditto-add ()
  "Add a new issue."
  (interactive)
  (ditto-call-process "add" nil "pop"))

(defun ditto-status ()
  "Show status of issues."
  (interactive)
  (ditto-call-process "status" nil "display"))

(defun ditto-show-release ()
  "show issues for release."
  (interactive)

  (setq release-name (ditto-extract-thing-at-point ditto-release-name-regex 2))
    (if release-name
        (ditto-call-process "release-summary" (concat "-r" release-name) "switch")
      (error "release name not found")))

(defun ditto-todo ()
  "Show current todo."
  (interactive)
  (ditto-call-process "list-releases" nil "pop"))

(defun ditto-todo-org ()
  "Show current todo in org-mode compatible format"
  (interactive)
  (ditto-call-process "time-release-org" nil "pop"))

(defun ditto-todo-org_no_time ()
  "Show current todo in org-mode compatible format with no time or status information"
  (interactive)
  (ditto-call-process "time-release-org-no-time" nil "pop"))

(defun ditto-log ()
  "Show log of recent activities."
  (interactive)
  (ditto-call-process "log" nil "pop"))

(defun ditto-order-up ()
  "Move issue up in the release"
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (ditto-call-process "order-up" issue-id)
      (error "Issue id not found"))))

(defun ditto-order-down ()
  "Move issue down in the release"
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (ditto-call-process "order-down" issue-id)
      (error "Issue id not found"))))

(defun ditto-edit ()
  "edit the issue in plain text"
  (interactive)
  (let ((issue-guid nil))
    (setq issue-guid (ditto-get-issue-id 1))
    (if issue-guid
	(find-file-other-window (concat ditto-last-visited-issue-directory "/issue-" issue-guid ".yaml"))
      (error "Issue id not found"))))

(defun ditto-show-issue()
  "Show issue details."
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (ditto-call-process "show" issue-id "switch")
      (error "Issue id not found"))))

(defun ditto-show ()
  "Show issue detale."
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (ditto-call-process "show" issue-id "switch")
      (error "Issue id not found"))))

(defun ditto-assign ()
  "Assign issue to a release."
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (ditto-call-process "assign" issue-id "switch")
      (error "Issue id not found"))))

(defun ditto-assignfeature ()
  "Assign issue to a feature."
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (ditto-call-process "assignfeature" issue-id "switch")
      (error "Issue id not found"))))

(defun ditto-set-feature-time ()
  "Set estimate for how long a feature will take."
  (interactive)
  (let ((feature-name nil))
    (setq feature-name (ditto-extract-thing-at-point ditto-feature-name-regex 2))
    (if feature-name
        (ditto-call-process "set-feature-time" feature-name "switch")
      (error "Feature name not found"))))

(defun ditto-unassign ()
  "Assign issue to a release."
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (ditto-call-process "unassign" issue-id "switch")
      (error "Issue id not found"))))

(defun ditto-comment ()
  "Edit issue comment."
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (ditto-call-process "comment" issue-id "switch")
      (error "Issue id not found"))))

(defun ditto-close ()
  "Close a issue."
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (ditto-call-process "close" issue-id "switch")
      (error "Issue id not found"))))

(defun ditto-claim ()
  "Claim a issue."
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (ditto-call-process "claim" issue-id "switch")
      (error "Issue id not found"))))

(defun ditto-drop ()
  "Drop an issue."
  (interactive)
  (let ((issue-id nil))
    (setq issue-id (ditto-get-issue-id 1))
    (if issue-id
        (when (yes-or-no-p (concat "Drop " issue-id " "))
          (ditto-call-process "drop" issue-id "switch"))
      (error "Issue id not found"))))

(defun ditto-release ()
  "Mark issues as released."
  (interactive)
  (let ((release-name nil))
    (setq release-name (ditto-extract-thing-at-point ditto-release-name-regex 2))
    (if release-name
        (ditto-call-process "release" release-name "switch")
      (error "Release name not found"))))

(defun ditto-release-feature ()
  "Mark issues as released."
  (interactive)
  (let ((feature-name nil))
    (setq feature-name (ditto-extract-thing-at-point ditto-feature-name-regex 2))
    (if feature-name
        (ditto-call-process "releasefeature" feature-name "switch")
      (error "Feature name not found"))))

(defun ditto-get-issue-id (n)
  "works in the todo view or in the issue view"
  (or (ditto-extract-thing-at-point ditto-issue-id-regex n) 
      (ditto-extract-thing-at-point ditto-issue-id-regex-in-issue n)))

(defun ditto-get-issue-guid (n)
  "often the guid is the same as the id"
  (or (ditto-extract-thing-at-point ditto-issue-guid-regex n)
      (ditto-extract-thing-at-point ditto-issue-id-regex-in-issue n)))

(defun ditto-extract-thing-at-point (regex n)
  (save-excursion
    (let ((line (buffer-substring-no-properties (progn (beginning-of-line) (point))
                                  (progn (end-of-line) (point)))))
      (when (string-match regex line)
        (match-string n line)))))

(defun ditto-reload ()
  (interactive)
  (let ((prev_line_number (line-number-at-pos)))
    (cond ((string= (buffer-name) "*ditto-todo*")
	   (ditto-call-process "todo" nil "switch" prev_line_number))
	  ((string= (buffer-name) "*ditto-time-release*")
	   (ditto-call-process "time-release" nil "switch" prev_line_number))
	  ((string= (buffer-name) "*ditto-status*")
	   (ditto-call-process "status" nil "switch" prev_line_number))
	  ((string= (buffer-name) "*ditto-log*")
	   (ditto-call-process "log" nil "switch" prev_line_number)))))


(defun ditto-close-buffer ()
  "Close ditto buffer."
  (interactive)
  (quit-window))

(defun ditto-call-process (command &optional arg popup-flag prev-line-number)
  "Call ditto process asynchronously according with sub-commands."
  (let* ((buffer (get-buffer-create (concat "*ditto-" command "*")))
         (proc (get-buffer-process buffer)))

    (if (and proc (eq (process-status proc) 'run))
        (when (y-or-n-p (format "A %s process is running; kill it?"
                                (process-name proc)))
          (interrupt-process proc)
          (sit-for 1)
          (delete-process proc))

    (with-current-buffer buffer
      (erase-buffer)
      (buffer-disable-undo (current-buffer)))

    (make-comint-in-buffer "ditto-call-process"
                           buffer shell-file-name nil shell-command-switch
                           (ditto-build-command command arg))

    (cond ((or (eq major-mode 'ditto-mode)
               (string= popup-flag "switch"))
           (switch-to-buffer buffer))
          ((string= popup-flag "pop")
           (pop-to-buffer buffer))
          ((string= popup-flag "display")
           (display-buffer buffer))
          (t
           (set-buffer buffer)))

    (setq ditto-prev-line-number prev-line-number)
    (set-process-sentinel
     (get-buffer-process buffer)
     '(lambda (process signal)
        (when (string= signal "finished\n")
          (with-current-buffer (process-buffer process)
            (ditto-mode)
            (goto-char (point-min))
	    (and ditto-prev-line-number (goto-line ditto-prev-line-number)))))))))

(defvar ditto-last-visited-issue-directory nil)

(defun ditto-build-command (command arg)
  (let (issue-directory current-directory)

    ;; Reserve current directory to come back later It's needed when
    ;; automatically finding directory.
    (when buffer-file-name
      (setq current-directory (file-name-directory (buffer-file-name))))

    (cond ((eq major-mode 'ditto-mode)
           (setq issue-directory ditto-last-visited-issue-directory))
          ((and (not (string= command "init"))
                ditto-find-issue-directory-automatically-flag
                (catch 'loop
                  (while t
                    (cond ((file-exists-p ditto-issue-directory)
                           (throw 'loop t))
                          ((string= "/" default-directory)
                           (throw 'loop nil))
                          (t
                           (cd ".."))))))
           (setq issue-directory
                            (concat default-directory ditto-issue-directory)))
          (t
           (setq issue-directory
                 (read-file-name "Issue dir: "
                                 (or ditto-last-visited-issue-directory
                                     default-directory)))))

    ;; Restore default directory if needed.
    (when current-directory
      (setq default-directory current-directory))

    (setq ditto-last-visited-issue-directory issue-directory)
    (mapconcat 'identity
               (list ditto-program ;;"-i" issue-directory 
		     ;;"--config-file" (concat issue-directory "/../.ditto-config")
		     ;;"--plugins-file" (concat issue-directory "/../.ditto-plugins")
		     command arg
		     "-z" issue-directory) " ")))

;; Hooks
(defvar ditto-mode-hook nil
  "*Hooks for Taskpaper major mode")

;; Keymap
(defvar ditto-mode-map (make-keymap)
  "*Keymap for Ditto major mode")

(define-key ditto-mode-map "r"    'ditto-show-release)
(define-key ditto-mode-map "s"    'ditto-show-issue)
;; (define-key ditto-mode-map "t"    'ditto-todo)
;; (define-key ditto-mode-map "o"    'ditto-todo-org)
;; (define-key ditto-mode-map "O"    'ditto-todo-org_no_time)
;; (define-key ditto-mode-map "s"    'ditto-show)
;; (define-key ditto-mode-map "\C-m" 'ditto-show)
;; (define-key ditto-mode-map "A"    'ditto-add)
;; (define-key ditto-mode-map "a"    'ditto-assign)
;; (define-key ditto-mode-map "w"    'ditto-assignfeature)
;; (define-key ditto-mode-map "U"    'ditto-unassign)
;; (define-key ditto-mode-map "D"    'ditto-drop)
;; (define-key ditto-mode-map "e"    'ditto-edit)
;; (define-key ditto-mode-map "+"    'ditto-comment)
;; (define-key ditto-mode-map "c"    'ditto-close)
;; (define-key ditto-mode-map "l"    'ditto-claim)
;; (define-key ditto-mode-map "r"    'ditto-release)
;; (define-key ditto-mode-map "Q"    'ditto-add-feature)
;; (define-key ditto-mode-map "\C-Q" 'ditto-release-feature)
;; (define-key ditto-mode-map "g"    'ditto-reload)
;; (define-key ditto-mode-map "q"    'ditto-close-buffer)
;; (define-key ditto-mode-map "u"    'ditto-order-up)
;; (define-key ditto-mode-map "d"    'ditto-order-down)
;; (define-key ditto-mode-map "E"    'ditto-edit)

;; Face
(defface ditto-issue-id-face
  '((((class color) (background light))
     (:foreground "slate gray" :underline t :weight bold))
    (((class color) (background dark))
     (:foreground "slate gray" :underline t :weight bold)))
  "Face definition for issue id")

(defface ditto-release-name-face
  '((((class color) (background light))
     (:foreground "red" :underline t :weight bold))
    (((class color) (background dark))
     (:foreground "red" :underline t :weight bold)))
  "Face definition for release name")

(defface ditto-issue-closed-name-face
  '((((class color) (background light))
     (:foreground "seashell4" :slant italic))
    (((class color) (background dark))
     (:foreground "seashell4" :slant italic)))
  "Face definition for closed issues")

(defface ditto-issue-text-closed-name-face
  '((((class color) (background light))
     (:foreground "seashell4" :slant italic))
    (((class color) (background dark))
     (:foreground "seashell4" :slant italic)))
  "Face definition for the text of closed issues")

(defface ditto-issue-open-name-face
  '((((class color) (background light))
     (:foreground "coral"))
    (((class color) (background dark))
     (:foreground "coral")))
  "Face definition for open issues")

(defface ditto-feature-issue-open-name-face
  '((((class color) (background light))
     (:foreground "palegreen"))
    (((class color) (background dark))
     (:foreground "palegreen")))
  "Face definition for open feature issues")

(defface ditto-issue-text-open-name-face
  '((((class color) (background light))
     (:foreground "coral"))
    (((class color) (background dark))
     (:foreground "coral")))
  "Face definition for the text of open issues")

(defvar ditto-issue-id-face 'ditto-issue-id-face)
(defvar ditto-release-name-face 'ditto-release-name-face)
(defvar ditto-issue-closed-name-face 'ditto-issue-closed-name-face)
(defvar ditto-issue-open-name-face 'ditto-issue-open-name-face)
(defvar ditto-issue-text-open-name-face 'ditto-issue-text-open-name-face)
(defvar ditto-feature-issue-open-name-face 'ditto-feature-issue-open-name-face)
(defvar ditto-issue-text-closed-name-face 'ditto-issue-text-closed-name-face)
(defvar ditto-font-lock-keywords
  '(("^[_ ]+\\([^:\n]+\\):.*$" (1 ditto-issue-id-face t))
    ("^Version *\\([^\n ]+\\) *.*$" (1 ditto-release-name-face t))
    ("^.*: \\(unstarted\\) :.*$" (1 ditto-issue-open-name-face t))
    ("^.*: \\(dev_done\\) :.*$" (1 ditto-issue-closed-name-face t))
    ("^.*: \\(qa_done\\) :.*$" (1 ditto-issue-closed-name-face t))
    ("^.*: \\(closed\\) :.*$" (1 ditto-issue-closed-name-face t))
    ("^.*:  unstarted :\\(.*\\)$" (1 ditto-issue-text-open-name-face t))
    ("^.*\\(F) unstarted :.*\\)$" (1 ditto-feature-issue-open-name-face t))
    ("^\\(:Feature:.*\\)$" (1 ditto-feature-issue-open-name-face t))
    ("^\\(---.*feature..*---.*\\)$" (1 ditto-feature-issue-open-name-face t))
    ("^.*: dev_done\\(.*\\)$" (1 ditto-issue-text-closed-name-face t))
    ("^.*: qa_done\\(.*\\)$" (1 ditto-issue-text-closed-name-face t))
    ("^.*: closed\\(.*\\)$" (1 ditto-issue-text-closed-name-face t))))

;; Ditto major mode
(define-derived-mode ditto-mode fundamental-mode "Ditto"
  "Major mode Ditto information."
  (interactive)
  (kill-all-local-variables)
  (setq major-mode 'ditto-mode)
  (setq mode-name "Ditto")
  (use-local-map ditto-mode-map)
  (set (make-local-variable 'font-lock-defaults)  '(ditto-font-lock-keywords))
  (font-lock-mode 1)
  (run-hooks 'ditto-mode-hook))

(provide 'ditto)
;;; ditto.el ends here


;;; Allow to copy links from org mode release buffer
(org-add-link-type "ditto" 'org-ditto-open)
(add-hook 'org-store-link-functions 'org-ditto-store-link)

(defun org-ditto-open (link)
  (when (string-match "\\(.*\\):\\([0-9]+\\)$"  link)
    (let* ((path (match-string 1 link))
           (page (string-to-number (match-string 2 link))))
      (org-open-file path 1) ;; let org-mode open the file (in-emacs = 1)
      ;; so that org-link-frame-setup is respected
      (doc-view-goto-page page)
      )))

(defun org-ditto-store-link ()
  "Store a link to a docview buffer"
  (when (eq major-mode 'ditto-mode)
    ;; This buffer is in ditto mode
    (let* ((path ditto-last-visited-issue-directory)
           (issue-id (trim-whitespace (ditto-extract-thing-at-point ditto-issue-id-regex 1)))
	   (issue-description (ditto-extract-thing-at-point ditto-issue-description-regex 1))
           (link (concat "elisp:(gtpmenu-ditto-goto-issue \"" path "\" \"" issue-id "\")"))
           (description ""))
      (org-store-link-props
       :type "ditto"
       :description (concat issue-id " " issue-description)
       :link link))))

;;;

