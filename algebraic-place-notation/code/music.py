
# only minor music for the moment
# tuples are:
#     (row, description, score)

#maybe score 65 at back badly!

score_for_music_at_backstroke = 4
score_for_65_at_backstroke = -4

music = {
    "654321" : ("backrounds", 6),
    "321654" : ("backrounds_lrflip", 5),
    "3456"   : ("almostrounds_1", 2),
    "1234"   : ("almostrounds_2", 2),
    "4321"   : ("almost_backrounds_1", 2),
    "6543"   : ("almost_backrounds_2", 2),
    "132456" : ("rounds_near_miss_1", 2),
    "124356" : ("rounds_near_miss_2", 2),
    "123546" : ("rounds_near_miss_3", 2),
    "123465" : ("rounds_near_miss_4", 2),
    "135246" : ("queens", 6),
    "642531" : ("queen_backwards", 5),
    "246135" : ("queens_lrflip", 5),
    "531642" : ("queen_backwards_lrflip", 5),
    "142536" : ("tittums", 7),
    "635241" : ("tittums_backwards", 5),
    "415263" : ("tittums_pairflip", 5),
}


#
# 135246 queens
# 246135 (queens, flipped)
# 642531 (back queens)
# 531642 (back queens, flipped)
# 654321 backrounds
# 321654 (backrounds flipped)
# 415263 (tittums, pair-flipped)

# only handling minor for now
def analyseMusic(rows):
    total_score = 0
    details = ""

    rowIdx = 0
    # don't analyse last row, it's rounds again
    for r in rows[:-1]:
        name = None

        if r in music:
            (name, score) = music[r]
            total_score += score

            if (rowIdx % 2) == 1:
                # it's backstroke
                total_score += score_for_music_at_backstroke
                name = name + " AT BACK"

        if name != None:
            details += "\n%s %s (row %d) %s" % (name, score, rowIdx, r)

        name = None

        if (rowIdx % 1) == 1:
            # it's backstroke
            if (r[4:] == "65"):
                name = "65 at back"
                score = score_for_65_at_backstroke
                total_score += score

        if name != None:
            details += "\n%s %s (row %d) %s" % (name, score, rowIdx, r)

        rowIdx += 1

    return (total_score, details)
