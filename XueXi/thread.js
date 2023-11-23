class Task {
	constructor(name, delay) {
		this.name = name;
		this.delay = delay || 0;
	}

	// overwrite this
	exec(resolve) {
		resolve();
	}
}

class Thread {
	constructor() {
		this.tasks = [];
		this.id = 0;
		this.curTask = null;
		this.curTaskBeginTime = 0;
	}

	start(intervalTime) {
		if (this.id != 0) {
			return;
		}
		let thiz = this;
		function wrapRun() {
			thiz._run();
		}
		this.curTaskBeginTime = Date.now();
		intervalTime = intervalTime || 300;
		this.id = setInterval(wrapRun, intervalTime);
	}

	_run () {
		if (this.curTask != null) {
			return;
		}
		if (this.tasks.length == 0) {
			return;
		}
		let topTask = this.tasks[0];
		let diffTime = Date.now() - this.curTaskBeginTime;
		if (diffTime < topTask.delay) {
			// console.log('Wait...');
			// wait
			return;
		}
		this.curTask = this.tasks.shift();
		let thiz = this;
		function _resolve_() {
			thiz._resolve();
		}
		// console.log('Thread.run ', this.curTask);
		this.curTask.exec(_resolve_);
	}

	_resolve() {
		this.curTask = null;
		this.curTaskBeginTime = Date.now();
	}

	stop() {
		clearInterval(this.id);
		this.id = 0;
		this.curTask = null;
		this.curTaskBeginTime = 0;
	}

	addTask(task) {
		this.tasks.push(task);
	}

	insertTask (idx, task) {
		this.tasks.splice(idx, 0, task);
	}

	clear() {
		this.tasks.length = 0;
	}
}

