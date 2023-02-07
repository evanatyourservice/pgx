from functools import partial
from typing import Tuple

import jax
import jax.numpy as jnp
from flax import struct
from flax.serialization import from_bytes

TRUE = jnp.bool_(True)
FALSE = jnp.bool_(False)


# 指し手のdataclass
@struct.dataclass
class JaxAnimalShogiAction:
    # 上の3つは移動と駒打ちで共用
    # 下の3つは移動でのみ使用
    # 駒打ちかどうか
    is_drop: jnp.ndarray = FALSE
    # piece: 動かした(打った)駒の種類
    piece: jnp.ndarray = jnp.int32(0)
    # final: 移動後の座標
    to: jnp.ndarray = jnp.int32(0)
    # 移動前の座標
    from_: jnp.ndarray = jnp.int32(0)
    # captured: 取られた駒の種類。駒が取られていない場合は0
    captured: jnp.ndarray = jnp.int32(0)
    # is_promote: 駒を成るかどうかの判定
    is_promote: jnp.ndarray = FALSE


INIT_BOARD = jnp.array(
    [
        [0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    dtype=jnp.bool_,
)


# POINT_MOVES: 座標と駒の種類から到達できる座標を列挙
# <EMPTY>, BLACK_PAWN, ROOK, BISHOP, KING, BLACK_GOLD, WHITE_PAWN, ROOK, BISHOP, KING, WHITE_GOLD
# Generated by workspace/animal-shogi-cache.py
BYTES = b"\xc8\x06>\x01\x93\x94\x0c\x0b\x03\x04\xa4bool\xc5\x060\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01\x01\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01\x01\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01\x01\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01\x01\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x01\x00\x00\x00\x01\x00\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x01\x00\x00\x00\x01\x00\x00\x01\x01\x00\x00\x01\x01\x00\x00\x00\x01\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01\x01\x01\x00\x01\x00\x01\x00\x01\x01\x01\x00\x01\x01\x00\x00\x01\x00\x01\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01\x01\x01\x00\x01\x00\x01\x00\x01\x01\x01\x00\x00\x01\x01\x00\x01\x00\x01\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01\x01\x01\x00\x01\x00\x01\x00\x01\x01\x01\x00\x01\x01\x00\x00\x01\x00\x01\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x01\x01\x01\x00\x01\x00\x01\x00\x01\x01\x01\x00\x00\x01\x01\x00\x01\x00\x01\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x01\x01\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x01\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x01\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x01\x01\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x01\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x01\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x01\x01\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x00"
POINT_MOVES = from_bytes(jnp.zeros((12, 11, 3, 4), dtype=jnp.bool_), BYTES)
POINT_MOVES = jnp.array(POINT_MOVES)
BYTES = b"\xc8\x01u\x01\x93\x92\x02\xcc\xb4\xa4bool\xc5\x01h\x00\x00\x01\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
LEGAL_ACTION_MASKS = from_bytes(jnp.zeros((2, 180), dtype=jnp.bool_), BYTES)
LEGAL_ACTION_MASKS = jnp.array(LEGAL_ACTION_MASKS)


# 盤面のdataclass
@struct.dataclass
class JaxAnimalShogiState:
    # turn 先手番なら0 後手番なら1
    turn: jnp.ndarray = jnp.int32(0)
    # board 盤面の駒。
    # 空白,先手ヒヨコ,先手キリン,先手ゾウ,先手ライオン,先手ニワトリ,後手ヒヨコ,後手キリン,後手ゾウ,後手ライオン,後手ニワトリ
    # の順で駒がどの位置にあるかをone_hotで記録
    # ヒヨコ: Pawn, キリン: Rook, ゾウ: Bishop, ライオン: King, ニワトリ: Gold　と対応
    board: jnp.ndarray = INIT_BOARD  # (11, 12)
    # hand 持ち駒。先手ヒヨコ,先手キリン,先手ゾウ,後手ヒヨコ,後手キリン,後手ゾウの6種の値を増減させる
    hand: jnp.ndarray = jnp.zeros(6, dtype=jnp.int8)
    # legal_actions_black/white: 自殺手や王手放置などの手も含めた合法手の一覧
    # move/dropによって変化させる
    legal_actions_black: jnp.ndarray = LEGAL_ACTION_MASKS[0]
    legal_actions_white: jnp.ndarray = LEGAL_ACTION_MASKS[1]
    # checked: ターンプレイヤーの王に王手がかかっているかどうか
    is_check: jnp.ndarray = FALSE
    # checking_piece: ターンプレイヤーに王手をかけている駒の座標
    checking_piece: jnp.ndarray = jnp.zeros(12, dtype=jnp.bool_)


def init(rng: jax.random.KeyArray) -> JaxAnimalShogiState:
    # TODO: use rng
    return JaxAnimalShogiState()


def step(
    state: JaxAnimalShogiState, action: int
) -> Tuple[JaxAnimalShogiState, int, bool]:
    # state, 勝敗判定,終了判定を返す
    reward = 0
    terminated = False
    legal_actions = _legal_actions(state)
    # 合法手が存在しない場合、手番側の負けで終了
    # 途中でreturnができないならどちらにしろ非合法な手ではじかれるから要らない？
    # actionが合法手でない場合、手番側の負けで終了
    # actionのfromが盤外に存在すると挙動がおかしくなるのでそれもここではじいておく
    _action = _dlaction_to_action(action, state)
    reward = jax.lax.cond(
        (_action.from_ > 11)
        | (_action.from_ < 0)
        | (legal_actions[_action_to_dlaction(_action, state.turn)] == 0),
        lambda: _turn_to_reward(_another_color(state)),
        lambda: reward,
    )
    terminated = jax.lax.cond(
        (_action.from_ > 11)
        | (_action.from_ < 0)
        | (legal_actions[_action_to_dlaction(_action, state.turn)] == 0),
        lambda: True,
        lambda: terminated,
    )
    # actionが合法手の場合
    state = jax.lax.cond(
        terminated,
        lambda: state,
        lambda: jax.lax.cond(
            _action.is_drop == 1,
            lambda: _drop(_update_legal_drop_actions(state, _action), _action),
            lambda: _move(_update_legal_move_actions(state, _action), _action),
        ),
    )
    # トライルールによる勝利判定
    reward = jax.lax.cond(
        ~terminated & _is_try(_action),
        lambda: _turn_to_reward(state.turn),
        lambda: reward,
    )
    terminated = jax.lax.cond(
        _is_try(_action),
        lambda: True,
        lambda: terminated,
    )
    turn = _another_color(state)
    state = state.replace(turn=turn)  # type: ignore
    no_checking_piece = jnp.zeros(12, dtype=jnp.int32)
    # 王手をかけている駒は直前に動かした駒であるはず
    checking_piece = no_checking_piece.at[_action.to].set(TRUE)
    state = jax.lax.cond(
        (_is_check(state)) & (terminated is False),
        lambda: state.replace(  # type: ignore
            is_check=TRUE,
            checking_piece=checking_piece,
        ),
        lambda: state.replace(  # type: ignore
            is_check=FALSE,
            checking_piece=no_checking_piece,
        ),
    )
    return state, reward, terminated


def _turn_to_reward(turn) -> int:
    reward = jax.lax.cond(
        turn == 0,
        lambda: 1,
        lambda: -1,
    )
    return reward


# dlshogiのactionはdirection(動きの方向)とto（駒の処理後の座標）に依存
def _dlshogi_action(direction, to) -> int:
    return direction * 12 + to


# fromの座標とtoの座標からdirを生成
def _point_to_direction(_from, to, promote, turn):
    dis = to - _from
    # 後手番の動きは反転させる
    dis = jax.lax.cond(turn == 1, lambda: -dis, lambda: dis)
    # UP, UP_LEFT, UP_RIGHT, LEFT, RIGHT, DOWN, DOWN_LEFT, DOWN_RIGHT, UP_PROMOTE... の順でdirを割り振る
    # PROMOTEの場合は+8する処理を入れるが、どうぶつ将棋ではUP_PROMOTEしか存在しない(はず)
    # dir:  0  1  2  3  4  5  6  7
    # dis: -1  3 -5  4 -4  1  5 -3
    base = 5
    to_dir = jnp.int32(
        # -5 -4 -3 -2 -1 0 1 2 3 4 5
        [2, 4, 7, -1, 0, -1, 5, -1, 1, 3, 6]
    )
    direction = to_dir[base + dis]
    direction = jax.lax.cond(
        promote == 1, lambda: direction + 8, lambda: direction
    )
    return direction


# 打った駒の種類をdirに変換
def _hand_to_direction(piece) -> int:
    # 移動のdirはPROMOTE_UPの8が最大なので9以降に配置
    # 9: 先手ヒヨコ 10: 先手キリン... 14: 後手ゾウ　に対応させる
    return jax.lax.cond(piece <= 5, lambda: 8 + piece, lambda: 6 + piece)


# AnimalShogiActionをdlshogiのint型actionに変換
def _action_to_dlaction(action: JaxAnimalShogiAction, turn) -> int:
    return jax.lax.cond(
        action.is_drop,
        lambda: _dlshogi_action(_hand_to_direction(action.piece), action.to),
        lambda: _dlshogi_action(
            _point_to_direction(
                action.from_, action.to, action.is_promote, turn
            ),
            action.to,
        ),
    )


# dlshogiのint型actionをdirectionとtoに分解
def _separate_dlaction(action: int) -> Tuple[int, int]:
    # direction, to の順番
    return action // 12, action % 12


# directionからfromがtoからどれだけ離れてるかと成りを含む移動かを得る
# 手番の情報が必要
def _direction_to_from(direction, to, turn) -> Tuple[int, int]:
    to_diff = jnp.int32(
        # 0  1   2  3   4  5  6   7   8  9
        [-1, 3, -5, 4, -4, 1, 5, -3, -1, 0, 0, 0, 0, 0, 0]
    )
    is_promote = jax.lax.cond(direction >= 8, lambda: TRUE, lambda: FALSE)
    dif = to_diff[direction]
    _from = jax.lax.cond(turn == 0, lambda: to - dif, lambda: to + dif)
    return _from, is_promote


def _direction_to_hand(direction: int) -> int:
    return jax.lax.cond(
        direction <= 11, lambda: direction - 8, lambda: direction - 6
    )


def _dlmoveaction_to_action(
    action: int, state: JaxAnimalShogiState
) -> JaxAnimalShogiAction:
    direction, to = _separate_dlaction(action)
    _from, is_promote = _direction_to_from(direction, to, state.turn)
    piece = _piece_type(state, _from)
    captured = _piece_type(state, to)
    return JaxAnimalShogiAction(
        is_drop=FALSE,
        piece=piece,
        to=to,
        from_=_from,
        captured=captured,
        is_promote=is_promote,
    )  # type: ignore


def _dldropaction_to_action(action: int) -> JaxAnimalShogiAction:
    direction, to = _separate_dlaction(action)
    piece = _direction_to_hand(direction)
    return JaxAnimalShogiAction(
        is_drop=TRUE, piece=piece, to=to
    )  # type: ignore


def _dlaction_to_action(
    action: int, state: JaxAnimalShogiState
) -> JaxAnimalShogiAction:
    direction, to = _separate_dlaction(action)
    return jax.lax.cond(
        direction <= 8,
        lambda: _dlmoveaction_to_action(action, state),
        lambda: _dldropaction_to_action(action),
    )


# 手番側でない色を返す
def _another_color(state: JaxAnimalShogiState) -> jnp.ndarray:
    return (state.turn + 1) % 2


# 相手の駒を同じ種類の自分の駒に変換する
def _convert_piece(piece):
    # 空白,先手ヒヨコ,先手キリン,先手ゾウ,先手ライオン,先手ニワトリ,後手ヒヨコ,後手キリン,後手ゾウ,後手ライオン,後手ニワトリ
    return jnp.int32([-1, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5])[piece]


# 駒から持ち駒への変換
# 先手ひよこが0、後手ぞうが5
def _piece_to_hand(piece):
    # piece: 空白,先手ヒヨコ,先手キリン,先手ゾウ,先手ライオン,先手ニワトリ,後手ヒヨコ,後手キリン,後手ゾウ,後手ライオン,後手ニワトリ
    # hand 持ち駒。先手ヒヨコ,先手キリン,先手ゾウ,後手ヒヨコ,後手キリン,後手ゾウの6種の値を増減させる
    return jnp.int32([-1, 0, 1, 2, -1, -1, 3, 4, 5, -1, -1])[piece]


#  移動の処理
def _move(
    state: JaxAnimalShogiState,
    action: JaxAnimalShogiAction,
) -> JaxAnimalShogiState:
    board = state.board
    hand = state.hand
    board = board.at[action.piece, action.from_].set(FALSE)
    board = board.at[0, action.from_].set(TRUE)
    board = board.at[action.captured, action.to].set(FALSE)
    board = jax.lax.cond(
        action.is_promote == 1,
        lambda: board.at[action.piece + 4, action.to].set(TRUE),
        lambda: board.at[action.piece, action.to].set(TRUE),
    )
    hand = jax.lax.cond(
        action.captured == 0,
        lambda: hand,
        lambda: hand.at[_piece_to_hand(_convert_piece(action.captured))].set(
            hand[_piece_to_hand(_convert_piece(action.captured))] + 1
        ),
    )
    return state.replace(  # type: ignore
        board=board,
        hand=hand,
    )


#  駒打ちの処理
def _drop(
    state: JaxAnimalShogiState, action: JaxAnimalShogiAction
) -> JaxAnimalShogiState:
    board = state.board
    hand = state.hand
    n = hand[_piece_to_hand(action.piece)]
    hand = hand.at[_piece_to_hand(action.piece)].set(n - 1)
    board = board.at[action.piece, action.to].set(TRUE)
    board = board.at[0, action.to].set(FALSE)
    return state.replace(  # type: ignore
        board=board,
        hand=hand,
    )


#  ある座標に存在する駒種を返す
def _piece_type(state: JaxAnimalShogiState, point: int) -> jnp.ndarray:
    return state.board[:, point].argmax()


# ある駒の持ち主を返す
def _owner(piece):
    # 空白,先手ヒヨコ,先手キリン,先手ゾウ,先手ライオン,先手ニワトリ,後手ヒヨコ,後手キリン,後手ゾウ,後手ライオン,後手ニワトリ
    return jnp.int32([2, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1])[piece]


# 盤面のどこに何の駒があるかをnp.arrayに移したもの
# 同じ座標に複数回piece_typeを使用する場合はこちらを使った方が良い
def _board_status(state: JaxAnimalShogiState) -> jnp.ndarray:
    return state.board.argmax(axis=0)  # (11,12) => (12,)


# 駒の持ち主の判定
def _pieces_owner(state: JaxAnimalShogiState) -> jnp.ndarray:
    pieces = _board_status(state)  # (12,)
    return jax.vmap(_owner)(pieces)


# 利きの判定
def _effected_positions(state: JaxAnimalShogiState, turn) -> jnp.ndarray:
    pieces = _board_status(state)
    owners = _pieces_owner(state)  # (12,)
    _from = jnp.arange(12)
    effects = POINT_MOVES[_from, pieces].reshape(12, 12)
    mask = jnp.tile(owners == turn, (12, 1)).transpose()  # (12, 12)
    effects = jnp.where(mask, effects, FALSE)
    all_effects = effects.sum(axis=0)  # bool => integer
    return all_effects  # (12,)


# 王手の判定(turn側の王に王手がかかっているかを判定)
def _is_check(state: JaxAnimalShogiState):
    effects = _effected_positions(state, _another_color(state))
    king_location = state.board[4 + 5 * state.turn, :].argmax()
    return effects[king_location] != 0


# 成る動きが合法かどうかの判定
def _can_promote(to: int, piece: int) -> bool:
    return ((piece == 1) & (to % 4 == 0)) | ((piece == 6) & (to % 4 == 3))


# 駒の種類と位置から生成できるactionのフラグを立てる
def _create_piece_actions(_from: int, piece: int) -> jnp.ndarray:
    turn = _owner(piece)
    actions = jnp.zeros((15, 12), dtype=jnp.bool_)
    can_move_to = POINT_MOVES[_from, piece].reshape(12)
    to = jnp.arange(12)
    normal_dir = jax.vmap(
        partial(_point_to_direction, _from=_from, promote=False, turn=turn)
    )(to=to)
    promote_dir = jax.vmap(
        partial(_point_to_direction, _from=_from, promote=True, turn=turn)
    )(to=to)
    can_promote = jax.vmap(partial(_can_promote, piece=piece))(to=to)
    actions = actions.at[normal_dir, to].set(can_move_to)
    actions = actions.at[promote_dir, to].set(can_move_to & can_promote)
    return actions.flatten()


# 駒の種類と位置から生成できるactionのフラグを立てる
def _add_move_actions(_from, piece, array: jnp.ndarray) -> jnp.ndarray:
    actions = _create_piece_actions(_from, piece)
    return array | actions


# 駒の種類と位置から生成できるactionのフラグを折る
def _filter_move_actions(_from, piece, array: jnp.ndarray) -> jnp.ndarray:
    actions = _create_piece_actions(_from, piece)
    return array & ~actions


# 駒打ちのactionを追加する
def _add_drop_actions(piece: int, array: jnp.ndarray) -> jnp.ndarray:
    direction = _hand_to_direction(piece)
    actions = array.reshape(15, 12)
    actions = actions.at[direction, :].set(TRUE)
    return actions.flatten()


# 駒打ちのactionを消去する
def _filter_drop_actions(piece, array: jnp.ndarray) -> jnp.ndarray:
    direction = _hand_to_direction(piece)
    actions = array.reshape(15, 12)
    actions = actions.at[direction, :].set(FALSE)
    return actions.flatten()


# stateからblack,white両方のlegal_actionsを生成する
# 普段は使わないがlegal_actionsが設定されていない場合に使用
def _init_legal_actions(
    state: JaxAnimalShogiState = JaxAnimalShogiState(),
) -> JaxAnimalShogiState:
    pieces = _board_status(state)
    legal_black = jnp.zeros(180, dtype=jnp.bool_)
    legal_white = jnp.zeros(180, dtype=jnp.bool_)
    # 移動の追加
    legal_black = jax.lax.fori_loop(
        0,
        12,
        lambda i, x: jax.lax.cond(
            _owner(pieces[i]) == 0,
            lambda: _add_move_actions(i, pieces[i], x),
            lambda: x,
        ),
        legal_black,
    )
    legal_white = jax.lax.fori_loop(
        0,
        12,
        lambda i, x: jax.lax.cond(
            _owner(pieces[i]) == 1,
            lambda: _add_move_actions(i, pieces[i], x),
            lambda: x,
        ),
        legal_white,
    )
    # 駒打ちの追加
    for i in range(3):
        legal_black = jax.lax.cond(
            state.hand[i] == 0,
            lambda: legal_black,
            lambda: _add_drop_actions(1 + i, legal_black),
        )
        legal_white = jax.lax.cond(
            state.hand[i + 3] == 0,
            lambda: legal_white,
            lambda: _add_drop_actions(6 + i, legal_white),
        )
    return state.replace(  # type: ignore
        legal_actions_black=legal_black,
        legal_actions_white=legal_white,
    )


# 駒の移動によるlegal_actionsの更新
def _update_legal_move_actions(
    state: JaxAnimalShogiState, action: JaxAnimalShogiAction
) -> JaxAnimalShogiState:
    legal_action_masks = jnp.stack(
        [state.legal_actions_black, state.legal_actions_white]
    )
    player_actions = legal_action_masks[state.turn]
    enemy_actions = legal_action_masks[1 - state.turn]

    # 元の位置にいたときのフラグを折る
    player_actions = _filter_move_actions(
        action.from_, action.piece, player_actions
    )
    # 移動後の位置からの移動のフラグを立てる
    player_actions = _add_move_actions(action.to, action.piece, player_actions)
    # 駒が取られた場合、相手の取られた駒によってできていたactionのフラグを折る
    enemy_actions = jax.lax.cond(
        action.captured == 0,
        lambda: enemy_actions,
        lambda: _filter_move_actions(
            action.to, action.captured, enemy_actions
        ),
    )

    captured = _convert_piece(action.captured)
    captured = jax.lax.cond(
        captured % 5 == 0, lambda: captured - 4, lambda: captured
    )
    player_actions = jax.lax.cond(
        # capturedは何も取っていない場合は-1に変換されているはず
        captured == -1,
        lambda: player_actions,
        lambda: _add_drop_actions(captured, player_actions),
    )

    legal_action_masks = jnp.stack([player_actions, enemy_actions])
    return state.replace(  # type: ignore
        legal_actions_black=legal_action_masks[state.turn],
        legal_actions_white=legal_action_masks[1 - state.turn],
    )


# 駒打ちによるlegal_actionsの更新
def _update_legal_drop_actions(
    state: JaxAnimalShogiState, action: JaxAnimalShogiAction
) -> JaxAnimalShogiState:
    player_actions = jax.lax.cond(
        state.turn == 0,
        lambda: state.legal_actions_black,
        lambda: state.legal_actions_white,
    )
    # 移動後の位置からの移動のフラグを立てる
    player_actions = _add_move_actions(action.to, action.piece, player_actions)
    # 持ち駒がもうない場合、その駒を打つフラグを折る
    player_actions = jax.lax.cond(
        state.hand[_piece_to_hand(action.piece)] == 1,
        lambda: _filter_drop_actions(action.piece, player_actions),
        lambda: player_actions,
    )
    return jax.lax.cond(
        state.turn == 0,
        lambda: state.replace(  # type: ignore
            legal_actions_black=player_actions,
        ),
        lambda: state.replace(  # type: ignore
            legal_actions_white=player_actions,
        ),  # type: ignore
    )


# 自分の駒がある位置への移動を除く
def _filter_my_piece_move_actions(
    turn, owner: jnp.ndarray, array: jnp.ndarray
) -> jnp.ndarray:
    """
    owner[i] == turn
          i
    x x x F x x x
    x x x F x x x
    x x x F x x x
    --- 9
    x x x x x x x
    x x x x x x x
    """
    actions = array.reshape((15, 12))
    mask = jnp.tile(owner == turn, reps=(15, 1))  # (15,12)
    mask = mask.at[9:].set(FALSE)
    actions = jnp.where(mask, FALSE, actions)
    return actions.flatten()


# 駒がある地点への駒打ちを除く
def _filter_occupied_drop_actions(
    turn, owner: jnp.ndarray, array: jnp.ndarray
) -> jnp.ndarray:
    """
    owner[i] != 2
          i
    x x x x x x x
    x x x x x x x
    --- 9 (turn == 0)
    x x x F x x x
    x x x F x x x
    x x x F x x x
    --- 9 + 3 (turn == 0)
    x x x x x x x
    x x x x x x x
    """
    actions = array.reshape((15, 12))
    mask1 = jnp.tile(owner != 2, reps=(15, 1))  # (15,12)
    idx = jnp.arange(15)
    mask2 = jnp.tile(
        (9 + 3 * turn <= idx) & (idx < 12 + 3 * turn), reps=(12, 1)
    ).transpose()  # (15,12)
    mask = mask1 & mask2
    actions = jnp.where(mask, FALSE, actions)
    return actions.flatten()


# 自殺手を除く
def _filter_suicide_actions(
    turn, king_sq, effects: jnp.ndarray, array: jnp.ndarray
) -> jnp.ndarray:
    moves = POINT_MOVES[king_sq, 4].reshape(12)
    for i in range(12):
        array = jax.lax.cond(
            (moves[i] == 0) | (effects[i] == 0),
            lambda: array,
            lambda: array.at[
                _dlshogi_action(
                    _point_to_direction(king_sq, i, False, turn), i
                )
            ].set(FALSE),
        )
    return array


# 王手放置を除く
def _filter_leave_check_actions(
    turn, king_sq, check_piece: jnp.ndarray, array: jnp.ndarray
) -> jnp.ndarray:
    moves = POINT_MOVES[king_sq, 4].reshape(12)
    array = array.reshape((15, 12))

    # 駒打ちのフラグは全て折る
    array = array.at[8:, :].set(FALSE)
    # 王手をかけている駒の場所以外への移動ははじく
    array = jnp.where(
        jnp.tile(check_piece == 0, reps=(15, 1)), FALSE, array  # (15, 12)
    )

    for i in range(12):
        # 玉の移動はそれ以外でも可能だがフラグが折れてしまっているので立て直す
        array = jax.lax.cond(
            moves[i] == 0,
            lambda: array,
            lambda: array.at[
                _point_to_direction(king_sq, i, False, turn), i
            ].set(TRUE),
        )
    return array.flatten()


# boardのlegal_actionsを利用して合法手を生成する
def _legal_actions(state: JaxAnimalShogiState) -> jnp.ndarray:
    turn = state.turn
    action_array = jax.lax.cond(
        turn == 0,
        lambda: state.legal_actions_black,
        lambda: state.legal_actions_white,
    )
    king_sq = state.board[4 + 5 * turn].argmax()
    # 王手放置を除く
    action_array = jax.lax.cond(
        state.is_check == 1,
        lambda: _filter_leave_check_actions(
            turn, king_sq, state.checking_piece, action_array
        ),
        lambda: action_array,
    )
    own = _pieces_owner(state)
    # 自分の駒がある位置への移動actionを除く
    action_array = _filter_my_piece_move_actions(turn, own, action_array)
    # 駒がある地点への駒打ちactionを除く
    action_array = _filter_occupied_drop_actions(turn, own, action_array)
    # 自殺手を除く
    effects = _effected_positions(state, _another_color(state))
    action_array = _filter_suicide_actions(
        turn, king_sq, effects, action_array
    )
    # その他の反則手を除く
    # どうぶつ将棋の場合はなし
    return action_array


# トライルールによる勝利判定
# 王が最奥に動くactionならTrue
def _is_try(action: JaxAnimalShogiAction):
    return ((action.piece == 4) & (action.to % 4 == 0)) | (
        (action.piece == 9) & (action.to % 4 == 3)
    )
