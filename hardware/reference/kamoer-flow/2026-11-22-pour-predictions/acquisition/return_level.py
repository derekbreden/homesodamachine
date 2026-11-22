"""Bring the settled syrup back to its first photographed level and verify the appliance state."""
import time
from board import Board, Journal
from lab import HERE, WINDOWS, scan
from pours import REF, REF_ML, USB, arrange, restore, window


def return_level():
    journal = Journal(HERE / 'return.jsonl')
    reference = scan(REF)
    board = Board(USB, journal)
    try:
        at = arrange(board, journal, 'home', REF_ML)
        for index in range(4):
            error_ml = REF_ML - at['operating_ml']
            if abs(error_ml) < 0.28:
                break
            head = 'B' if error_ml > 0 else 'A'
            duration = round(max(25, min(160, 80 * abs(error_ml))))
            journal.append('home_trim', head=head, error_in_positioning_units=error_ml,
                           **board.gate(head, duration))
            time.sleep(3)
            at = window(f'home-trim-{index}', journal)
        time.sleep(9)
        end = window('home-settled', journal)
        lanes = scan(WINDOWS / end['label'])
        journal.append('station_position', first_window=REF.name, last_window=end['label'],
                       initial=reference, final=lanes,
                       displacement_native_px={str(a[0]):round(b[1]-a[1], 3) for a,b in zip(reference,lanes)})
        restore(board)
    finally:
        board.close()
        journal.append('closed')


if __name__ == '__main__':
    return_level()
