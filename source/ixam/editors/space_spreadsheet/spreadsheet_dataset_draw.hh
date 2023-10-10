/* SPDX-License-Identifier: GPL-2.0-or-later */

#pragma once

struct Panel;
struct bContext;

namespace ixam::ed::spreadsheet {

void spreadsheet_data_set_panel_draw(const bContext *C, Panel *panel);

}  // namespace ixam::ed::spreadsheet
