

function calculatePercentages(userInfoObj) {
    /*
		This function creates the stats for correct and incorrrect reading and meaning answers for radicals, kanji, and vocabulary.
		Futhermore, it generates the total and average corrent and incorrect precentages as well.
		The function excepts a json object and return a new json object with the stats.
	*/
	//Round number to second decimal point
	function roundNumber(Num) {
        return (Math.round((Num + 0.00001) * 10000) / 100);
    }

    percentageObj = {}

    //Meaning Stats
    percentageObj.kanjiMeaningCorrect = userInfoObj['kanji']['meaning_correct'];
    percentageObj.kanjiMeaningIncorrect = userInfoObj['kanji']['meaning_incorrect'];
    percentageObj.vocabMeaningCorrect = userInfoObj['vocab']['meaning_correct'];
    percentageObj.vocabMeaningIncorrect = userInfoObj['vocab']['meaning_incorrect'];
    percentageObj.radicalMeaningCorrect = userInfoObj['radical']['meaning_correct'];
    percentageObj.radicalMeaningIncorrect = userInfoObj['radical']['meaning_incorrect'];

    percentageObj.kanjiMeaningPercentage = roundNumber(userInfoObj['kanji']['meaning_correct'] / (userInfoObj['kanji']['meaning_correct'] + userInfoObj['kanji']['meaning_incorrect']));
    percentageObj.vocabMeaningPercentage = roundNumber(userInfoObj['vocab']['meaning_correct'] / (userInfoObj['vocab']['meaning_correct'] + userInfoObj['vocab']['meaning_incorrect']));
    percentageObj.radicalMeaningPercentage = roundNumber(userInfoObj['radical']['meaning_correct'] / (userInfoObj['radical']['meaning_correct'] + userInfoObj['radical']['meaning_incorrect']));

    //Reading Stats
    percentageObj.kanjiReadingCorrect = userInfoObj['kanji']['reading_correct'];
    percentageObj.kanjiReadingIncorrect = userInfoObj['kanji']['reading_incorrect'];
    percentageObj.vocabReadingCorrect = userInfoObj['vocab']['reading_correct'];
    percentageObj.vocabReadingIncorrect = userInfoObj['vocab']['reading_incorrect'];

    percentageObj.kanjiReadingPercentage = roundNumber(userInfoObj['kanji']['reading_correct'] / (userInfoObj['kanji']['reading_correct'] + userInfoObj['kanji']['reading_incorrect']));
    percentageObj.vocabReadingPercentage = roundNumber(userInfoObj['vocab']['reading_correct'] / (userInfoObj['vocab']['reading_correct'] + userInfoObj['vocab']['reading_incorrect']));

    //Total Stats
    percentageObj.totalMeaningCorrect = percentageObj.kanjiMeaningCorrect + percentageObj.vocabMeaningCorrect + percentageObj.radicalMeaningCorrect;
    percentageObj.totalMeaningIncorrect = percentageObj.kanjiMeaningIncorrect + percentageObj.vocabMeaningIncorrect + percentageObj.radicalMeaningIncorrect;
    percentageObj.totalMeaningPercentage = roundNumber(percentageObj.totalMeaningCorrect / (percentageObj.totalMeaningCorrect + percentageObj.totalMeaningIncorrect));

    percentageObj.totalReadingCorrect = percentageObj.kanjiReadingCorrect + percentageObj.vocabReadingCorrect;
    percentageObj.totalReadingIncorrect = percentageObj.kanjiReadingIncorrect + percentageObj.vocabReadingIncorrect;
    percentageObj.totalReadingPercentage = roundNumber(percentageObj.totalReadingCorrect / (percentageObj.totalReadingCorrect + percentageObj.totalReadingIncorrect));

    percentageObj.totalCorrect = percentageObj.totalMeaningCorrect + percentageObj.totalReadingCorrect;
    percentageObj.totalIncorrect = percentageObj.totalMeaningIncorrect + percentageObj.totalReadingIncorrect;
    percentageObj.totalPercentage = roundNumber(percentageObj.totalCorrect / (percentageObj.totalCorrect + percentageObj.totalIncorrect))

    //Average stats
    percentageObj.kanjiAveragePercentage = roundNumber((percentageObj.kanjiMeaningPercentage + percentageObj.kanjiReadingPercentage) / 2 / 100);
    percentageObj.radicalAveragePercentage = percentageObj.radicalMeaningPercentage;
    percentageObj.vocabAveragePercentage = roundNumber((percentageObj.vocabMeaningPercentage + percentageObj.vocabReadingPercentage) / 2 / 100);

    return percentageObj
}

function createPercentageTable(dataObj) {
	/*
		Creates a simple html table with data from the calculatePercentages function
	*/
    var table_ = $("<table></table>");
    table_.append("<tr><th></th><th>Reading</th><th>Meaning</th><th>Average/Sum</th></tr>");
    table_.append("<tr>" +
                                    "<td>Correct</td>" +
                                    "<td></td>" +
                                    "<td>" + dataObj.radicalMeaningPercentage + "</td>" +
                                    "<td>" + dataObj.radicalAveragePercentage + "</td></tr>");
    table_.append("<tr>" +
                                    "<td>Incorrect</td>" +
                                    "<td>" + dataObj.kanjiReadingPercentage + "</td>" +
                                    "<td>" + dataObj.kanjiMeaningPercentage + "</td>" +
                                    "<td>" + dataObj.kanjiAveragePercentage + "</td></tr>");
    table_.append("<tr>" +
                                    "<td>Accuracy</td>" +
                                    "<td>" + dataObj.vocabReadingPercentage + "</td>" +
                                    "<td>" + dataObj.vocabMeaningPercentage + "</td>" +
                                    "<td>" + dataObj.vocabAveragePercentage + "</td></tr>");
    table_.append("<tr><td colspan=\"4\">Overall</td></tr>");
    table_.append("<tr>" +
                                    "<td>Correct</td>" +
                                    "<td>" + dataObj.totalReadingCorrect + "</td>" +
                                    "<td>" + dataObj.totalMeaningCorrect + "</td>" +
                                    "<td>" + dataObj.totalCorrect + "</td></tr>");
    table_.append("<tr>" +
                                    "<td>Incorrect</td>" +
                                    "<td>" + dataObj.totalReadingIncorrect + "</td>" +
                                    "<td>" + dataObj.totalMeaningIncorrect + "</td>" +
                                    "<td>" + dataObj.totalIncorrect + "</td></tr>");
    table_.append("<tr>" +
                                    "<td>Accuracy</td>" +
                                    "<td>" + dataObj.totalReadingPercentage + "</td>" +
                                    "<td>" + dataObj.totalMeaningPercentage + "</td>" +
                                    "<td>" + dataObj.totalPercentage + "</td></tr>");
    $("#percentageChart").append(table_);
}

function createTimespent(unlockData) {
    var msecPerMinute = 1000 * 60;
    var msecPerHour = msecPerMinute * 60;
    var msecPerDay = msecPerHour * 24;

    dataArray = [];
    orderKeys = Object.keys(unlock_data).sort(function(a, b) { return a.split("_")[0] - b.split("_")[0] } );
	level_kanji = ['一', '二',　'三',　'四',　'五',
					'六',　'七',　'八',　'九',　'十',
                    '十一',　'十二',　'十三',　'十四',　'十五',
                    '十六',　'十七',　'十八',　'十九',　'二十',
                    '二十一',　'二十二',　'二十三',　'二十四',　'二十五',
                    '二十六',　'二十七',　'二十八',　'二十九',　'三十',
                    '三十一',　'三十二',　'三十三',　'三十四',　'三十五',
                    '三十六',　'三十七',　'三十八',　'三十九',　'四十',
                    '四十一',　'四十二',　'四十三',　'四十四',　'四十五',
                    '四十六',　'四十七',　'四十八',　'四十九',　'五十',
                    '五十一',　'五十二',　'五十三',　'五十四',　'五十五',
                    '五十六',　'五十七',　'五十八',　'五十九',　'六十'];

    for(var i = 0; i < orderKeys.length; i++) {
        temp = unlock_data[orderKeys[i]];
        date = temp.split(" ")[0] + "日" + temp.split(" ")[2].split(":")[0] + "時" + temp.split(" ")[2].split(":")[1] + "分";
        milli = (temp.split(" ")[0] * msecPerDay) + (temp.split(" ")[2].split(":")[0] * msecPerHour) + (temp.split(" ")[2].split(":")[1] * msecPerMinute);
        value = +(temp.split(" ")[0] + "." + temp.split(" ")[2].split(":")[0])
        dataArray.push({"level": level_kanji[i], "time": value,
                    "date": date, "milli": milli});
    }
    console.log(dataArray);
	return dataArray;
}

function createTimespentGraph(unlockData) {
	/*
		Creates a graph of time spent on a level over levels

	*/

	//Creating svg element
    var svg = d3.select('svg'),
    margin = {top: 60, right: 20, bottom: 45, left: 60},
    width = +svg.attr("width") - margin.left - margin.right,
    height = +svg.attr("height") - margin.top - margin.bottom;

	//Creating domain and range for x and y axis
    var x = d3.scaleBand().rangeRound([0, width]).padding(.1);
    var y = d3.scaleLinear().range([height, 0]);

	//Adding a transofmration
    var g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	//Creating values for my data based on the domain and range
    x.domain(unlockData.map(function(d) { return d.level; }));
    y.domain([0, d3.max(unlockData, function(d) { return d.time; })]);

	//Appending another g element from the one created earlier and adding a x-axis to it
    g.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + height + ")")
        .attr("writing-mode", "tb-rl")
        .call(d3.axisBottom(x).tickSize(0).tickPadding(10));

	//Appending a y axis to the element
    g.append("g")
        .attr("class", "axis axis--y")
        .call(d3.axisLeft(y).ticks(10))
        .append("text")
        //.attr("transform", "rotate(-90)")
        .attr("y", 270)
        .attr("x", -11)
        .attr("dx", "-2em")
        .attr("dy", "-1em")
        //.attr("writing-mode", "tb-rl")
        //.attr("text-orientation", "upright")
        .attr("text-anchor", "end")
		//.attr("class", "timeData")
		//.attr("fill", "white")
		//.append("span")
		.attr("class", "timeData")
        .text("Time Spent (Days)");

	//For each data, i select a non-existent .bar element and go enter the data and append a rectangle element to g eleemnt
    var bar = g.selectAll(".bar")
        .data(unlockData)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", function(d) { return x(d.level); })
		.attr("y", function(d) { return y(d.time); })
        .attr("width", x.bandwidth())
        .attr("height", function(d) { return height - y(d.time); })
        .text("Wanikani Levels");

	//For each data, i select a non-existent .lavel element and go enter the data and append a text element to g eleemnt
    var text = g.selectAll(".label")
        .data(unlockData).enter()
        .append("text");

	var textLabels = text
	    .attr("x", function(d) { return x(d.level); })
		.attr("y", function(d) { return (y(d.time) > 270 ? 250 : y(d.time)); })
		.attr("writing-mode", "tb-rl")
		.attr("dy", ".35em")
		.attr("dx", ".85em")
		.attr("class", "date-text")
		.text(function(d) { return d.date; })
		.attr("fill", "blue");

	g.append("line")
	    .style("stroke", "black")
	    .attr("x1", 0)
	    .attr("y1", y(15.5))
	    .attr("x2", width)
	    .attr("y2", y(15.5))

    return y;
}

function getLearnedCharacters(characterList) {
    kanjiLearned = characterList.kanji.characters_learned;
    radicalLearned = characterList.radical.characters_learned;
    vocabLearned = characterList.vocab.characters_learned;
   $("#learned").append("<span>" + radicalLearned + "部首 " + kanjiLearned + "漢字 "  + vocabLearned　+ "単語</span>")
}

function calculateEstimation(cTime, aTime) {
    var start = new Date(cTime.replace(" ", "T"));
    var average = new Date(aTime);
    var interval = Math.abs(dt - dt1);
}

function calculateAverageLevelTime(ms) {
    var milliToSecs = 1000

    var m = ms % milliToSecs;

    ms = (ms - m) / milliToSecs;

    var secs = ms  % 60;
    ms = (ms - secs) / 60;

    var mins = ms % 60;
    ms = (ms - mins) / 60;

    var hrs = ms % 24;
    ms = (ms - hrs) / 24;

    var days = ms
    return days + '日' + hrs + '時' + mins + '分'
}

function addOrRemove(bar_) {
   if ($(bar_).hasClass("removed")) {
      $(bar_).removeClass("removed");
   } else{
      $(bar_).addClass('removed');
   }
}

function updateAverages(time_) {
    class_ = ['#averageLevel', '#averTime']

    for (i = 0; i < class_.length; i++) {
        console.log('updating average ' + i + " " + time_)

        if (i == 0) {
            console.log("first 0")
            $(class_).text("Average Time: " + time_);
        }
        else if (! $(class_[i] + " span").length) {
            $(class_[i]).append("<span>" + time_ + "</span>");
        } else {
            $(class_[i] + " span").text(time_);
        }
    }
}
    var msecPerMinute = 1000 * 60;
    var msecPerHour = msecPerMinute * 60;
    var msecPerDay = msecPerHour * 24;

    dataObj = calculatePercentages(js_list);
    console.log(dataObj)
    createPercentageTable(dataObj)

    var unlock_data = js_list.unlock.timespent;

	var unlockData = createTimespent(unlock_data);

	dummy = {}
    dummy.currentLevel = js_list.user.level
    orderedKeys = Object.keys(js_list.unlock.timespent).sort(function(a, b) { return a.split("_")[0] - b.split("_")[0] } )
    temp = js_list.unlock.average;
    date = temp.split(" ")[0] + "日" + temp.split(" ")[2].split(":")[0] + "時" + temp.split(" ")[2].split(":")[1] + "分";
    $("#currLevelTime").append("<span>" + unlockData[orderedKeys.length-1].date + "</span>")
    $("#currLevel").append("<span>" + js_list.user.level + "</span>")
    $("#averTime").append("<span>" + date + "</span>");
    $("#startTime").append("<span>" + unlockData[0].date + "</span");
    $("#averageLevel").text("Average Time: " + date);

	curTime = js_list.unlock.date[orderedKeys.length];
	avgTime = js_list.unlock.average;

	console.log(orderedKeys.length)
	console.log(curTime);
	getLearnedCharacters(js_list)
	var yDomain = createTimespentGraph(unlockData);

	avgTimeMilli = (avgTime.split(" ")[0] * msecPerDay) + (avgTime.split(" ")[2].split(":")[0] * msecPerHour)
	                + (avgTime.split(" ")[2].split(":")[1] * msecPerMinute)


	fastestLevel = 0
    slowestLevel = 0
	$(".bar").each(function(i) {
	    if (unlockData[i].milli <= avgTimeMilli && i != unlockData.length-1) {
	        $(this).addClass("bar fastLevel");
	        if (unlockData[i].milli < unlockData[fastestLevel].milli) {
                fastestLevel = i
	        }
	    } else if (i != unlockData.length-1) {
	        $(this).addClass("bar slowLevel");
	        if (unlockData[i].milli > unlockData[slowestLevel].milli) {
	            slowestLevel = i
	        }
	    }
	})
	console.log("Slowest is " + slowestLevel + " Fastest Level is " + fastestLevel)
    $(".bar").eq(slowestLevel).addClass("slowest")
    $(".bar").eq(fastestLevel).addClass("fastest")
    $(".bar").eq(unlockData.length-1).addClass("current")
    //$(".bar").not(".current").click(function()
    $(".bar:not(.current)").click(function() {
        newTime = 0;
        j = 0;
        addOrRemove(this)
        $(".bar:not(.current)").each(function(i, d){
            if (! $(this).hasClass("removed")) {
                newTime += unlockData[i].milli
                j++;
            }
        })

        if (j != 0) {
            console.log(j)
            newAverage = calculateAverageLevelTime(newTime/j);
        } else {
            newAverage = calculateAverageLevelTime(avgTimeMilli);
        }
        console.log(newAverage);
        updateAverages(newAverage);

    });