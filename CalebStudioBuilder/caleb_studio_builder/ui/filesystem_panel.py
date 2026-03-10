from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLabel, QPushButton, QHBoxLayout, QAbstractItemView
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileSystemModel

class FilesystemPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header controls
        ctrl_layout = QHBoxLayout()
        ctrl_layout.addWidget(QLabel("<b>Filesystem Map</b>"))
        ctrl_layout.addStretch()
        
        self.btn_expand = QPushButton("+")
        self.btn_expand.setMaximumWidth(30)
        self.btn_expand.clicked.connect(self._expand_all)
        
        self.btn_collapse = QPushButton("-")
        self.btn_collapse.setMaximumWidth(30)
        self.btn_collapse.clicked.connect(self._collapse_all)
        
        ctrl_layout.addWidget(self.btn_expand)
        ctrl_layout.addWidget(self.btn_collapse)
        layout.addLayout(ctrl_layout)
        
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.currentPath()))
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        
        # Enable Drag and Drop
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QAbstractItemView.InternalMove)
        
        layout.addWidget(self.tree)

    def _expand_all(self):
        self.tree.expandAll()

    def _collapse_all(self):
        self.tree.collapseAll()
